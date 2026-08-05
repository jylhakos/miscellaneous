"""
Improved LSTM Inference Service with Enhanced Architecture
Scalable microservice for real-time time-series forecasting
"""

import sys
import json
import time
import datetime
import logging
from typing import Dict, List, Optional

import zmq
import numpy as np

from config import config
from lstm_model_manager import LSTMModelManager


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - [GPU-%(gpu_id)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class LSTMInferenceService:
    """
    LSTM Inference Microservice
    
    Responsibilities:
    - Consume time-series data from ZeroMQ queue
    - Run LSTM inference using trained models
    - Publish predictions to output queue
    - Handle errors and memory management
    """
    
    def __init__(self, gpu_id: int = 0):
        """
        Initialize LSTM Inference Service
        
        Args:
            gpu_id: GPU device ID
        """
        self.gpu_id = gpu_id
        self.model_manager = LSTMModelManager(gpu_id=gpu_id)
        
        # ZeroMQ sockets
        self.input_socket = None
        self.output_socket = None
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'total_inference_time': 0.0
        }
        
        # Initialize ZeroMQ connections
        self._setup_zmq()
        
        logger.info(f"LSTMInferenceService initialized on GPU {gpu_id}")
    
    def _setup_zmq(self):
        """Setup ZeroMQ PULL and PUSH sockets"""
        try:
            # Input socket (PULL from data collector)
            input_port = config.ZMQ_INPUT_PORT
            context_in = zmq.Context()
            self.input_socket = context_in.socket(zmq.PULL)
            self.input_socket.connect(f"tcp://localhost:{input_port}")
            logger.info(f"Connected to input queue: tcp://localhost:{input_port}")
            
            # Output socket (PUSH to output service)
            output_port = config.ZMQ_OUTPUT_PORTS[self.gpu_id]
            context_out = zmq.Context()
            self.output_socket = context_out.socket(zmq.PUSH)
            self.output_socket.setsockopt(zmq.LINGER, 1000)
            self.output_socket.setsockopt(zmq.SNDTIMEO, 5000)
            self.output_socket.bind(f"tcp://*:{output_port}")
            logger.info(f"Bound to output queue: tcp://*:{output_port}")
            
        except Exception as e:
            logger.error(f"ZeroMQ setup failed: {e}")
            raise
    
    def parse_message(self, msg: bytes) -> Optional[Dict]:
        """
        Parse incoming ZeroMQ message
        
        Args:
            msg: Raw message bytes
            
        Returns:
            Parsed message dictionary or None
        """
        try:
            msg_str = msg.decode('utf-8')
            data = json.loads(msg_str)
            
            # Validate required fields
            if 'FEATURE' not in data or 'INPUT_LIST' not in data:
                logger.error(f"Invalid message format: missing required fields")
                return None
            
            return data
            
        except Exception as e:
            logger.error(f"Message parsing failed: {e}")
            return None
    
    def extract_values_and_timestamps(self, input_list: List[Dict]) -> tuple:
        """
        Extract values and timestamps from input list
        
        Args:
            input_list: List of timestamp-value pairs
            
        Returns:
            Tuple of (values, timestamps, interval)
        """
        values = []
        timestamps = []
        
        for idx, item in enumerate(input_list):
            try:
                # Parse timestamp
                timestamp = int(item['TIMESTAMP'])
                timestamps.append(timestamp)
                
                # Parse value
                value = round(float(item['VALUE']), 2)
                values.append(value)
                
            except (KeyError, ValueError) as e:
                logger.error(f"Failed to parse item {idx}: {e}")
                return None, None, None
        
        # Calculate time interval
        if len(timestamps) >= 2:
            interval = abs(timestamps[0] - timestamps[1])
        else:
            interval = 900  # Default 15 minutes
        
        return values, timestamps, interval
    
    def calculate_next_timestamp(
        self,
        last_timestamp: int,
        interval: int
    ) -> datetime.datetime:
        """
        Calculate next prediction timestamp
        
        Args:
            last_timestamp: Last data timestamp (seconds since epoch)
            interval: Time interval in seconds
            
        Returns:
            Next timestamp as datetime
        """
        next_timestamp_sec = last_timestamp + interval
        next_dt = datetime.datetime.utcfromtimestamp(next_timestamp_sec)
        return next_dt
    
    def process_message(self, msg: bytes) -> bool:
        """
        Process incoming message and generate prediction
        
        Args:
            msg: Raw ZeroMQ message
            
        Returns:
            True if processing successful
        """
        start_time = time.time()
        
        try:
            # Parse message
            data = self.parse_message(msg)
            if data is None:
                return False
            
            feature = data['FEATURE']
            input_list = data['INPUT_LIST']
            
            logger.info(f"Processing feature: {feature}, data points: {len(input_list)}")
            
            # Validate input length
            if len(input_list) < config.MIN_INPUT_LENGTH:
                logger.warning(f"Insufficient data: {len(input_list)} < {config.MIN_INPUT_LENGTH}")
                return False
            
            # Extract values and timestamps
            values, timestamps, interval = self.extract_values_and_timestamps(input_list)
            if values is None:
                return False
            
            logger.debug(f"Values: {values}")
            
            # Run prediction
            prediction = self.model_manager.process_and_predict(feature, values)
            
            if prediction is None:
                logger.error("Prediction failed")
                self.stats['failed_predictions'] += 1
                return False
            
            # Calculate next timestamp
            next_timestamp = self.calculate_next_timestamp(timestamps[0], interval)
            next_timestamp_str = next_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # Send prediction to output queue
            self.send_prediction(next_timestamp_str, feature, prediction)
            
            # Update statistics
            inference_time = time.time() - start_time
            self.stats['successful_predictions'] += 1
            self.stats['total_inference_time'] += inference_time
            
            logger.info(
                f"Prediction successful - Feature: {feature}, "
                f"Value: {prediction:.4f}, Time: {next_timestamp_str}, "
                f"Inference: {inference_time:.4f}s"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Message processing failed: {e}", exc_info=True)
            self.stats['failed_predictions'] += 1
            return False
    
    def send_prediction(
        self,
        timestamp: str,
        feature: str,
        predicted_value: float
    ):
        """
        Send prediction to output queue
        
        Args:
            timestamp: Prediction timestamp
            feature: Feature name
            predicted_value: Predicted value
        """
        try:
            message = {
                'TIMESTAMP': timestamp,
                'FEATURE': feature,
                'PREDICTED': f"{predicted_value:.4f}"
            }
            
            self.output_socket.send_json(message)
            logger.debug(f"Prediction sent: {message}")
            
        except zmq.ZMQError as e:
            logger.error(f"Failed to send prediction: {e}")
    
    def print_statistics(self):
        """Print service statistics"""
        total = self.stats['total_processed']
        success = self.stats['successful_predictions']
        failed = self.stats['failed_predictions']
        total_time = self.stats['total_inference_time']
        
        if total > 0:
            success_rate = (success / total) * 100
            avg_time = total_time / success if success > 0 else 0
            
            logger.info(
                f"\n{'='*60}\n"
                f"Service Statistics (GPU {self.gpu_id}):\n"
                f"  Total Processed: {total}\n"
                f"  Successful: {success} ({success_rate:.2f}%)\n"
                f"  Failed: {failed}\n"
                f"  Average Inference Time: {avg_time:.4f}s\n"
                f"{'='*60}"
            )
    
    def run(self):
        """Main service loop"""
        logger.info(f"Starting LSTM Inference Service on GPU {self.gpu_id}")
        logger.info("Waiting for messages...")
        
        try:
            while True:
                try:
                    # Receive message with timeout
                    msg = self.input_socket.recv()
                    
                    # Process message
                    self.stats['total_processed'] += 1
                    self.process_message(msg)
                    
                    # Print statistics every 100 messages
                    if self.stats['total_processed'] % 100 == 0:
                        self.print_statistics()
                    
                except zmq.ZMQError as e:
                    logger.error(f"ZeroMQ error: {e}")
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    logger.info("Received shutdown signal")
                    break
                    
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
            
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up resources...")
        
        # Print final statistics
        self.print_statistics()
        
        # Cleanup model manager
        self.model_manager.cleanup()
        
        # Close sockets
        if self.input_socket:
            self.input_socket.close()
        if self.output_socket:
            self.output_socket.close()
        
        logger.info("Service shutdown complete")


def main():
    """Main entry point"""
    # Parse command line arguments
    gpu_id = 0
    if len(sys.argv) > 1:
        try:
            gpu_id = int(sys.argv[1])
            if gpu_id < 0 or gpu_id >= len(config.ZMQ_OUTPUT_PORTS):
                logger.error(f"Invalid GPU ID: {gpu_id}")
                sys.exit(1)
        except ValueError:
            logger.error(f"Invalid GPU ID argument: {sys.argv[1]}")
            sys.exit(1)
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create and run service
    service = LSTMInferenceService(gpu_id=gpu_id)
    service.run()


if __name__ == "__main__":
    main()
