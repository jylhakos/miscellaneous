
import sys

if sys.version_info < (3, 5):
    print(("ERROR: To use {} you need at least Python 3.5.\n" +
           "You are currently using Python {}.{}").format(sys.argv[0], *sys.version_info))
    sys.exit(1)

import logging
#import IPython
import DateTime

import os
#import colorama

import asyncio

from concurrent import futures

import grpc

from event_handler.examples.python.helloworld import helloworld_pb2

from event_handler.examples.python.helloworld import helloworld_pb2_grpc

from argparse import ArgumentParser

import traitlets.config

from aci.aci_uart import Uart
from aci.aci_utils import STATUS_CODE_LUT
from aci.aci_config import ApplicationConfig
import aci.aci_cmd as cmd
import aci.aci_evt as evt

from mesh import access
from mesh.provisioning import Provisioner, Provisionee  # NOQA: ignore unused import
from mesh import types as mt                            # NOQA: ignore unused import
from mesh.database import MeshDB                        # NOQA: ignore unused import
from models.config import ConfigurationClient           # NOQA: ignore unused import
from models.generic_on_off import GenericOnOffClient    # NOQA: ignore unused import
from models.generic_level import GenericLevelClient
from models.ctl import CTL


LOG_DIR = os.path.join(os.path.dirname(sys.argv[0]), "log")

USAGE_STRING = \
    """
    {c_default}{c_text}To control your device, use {c_highlight}d[x]{c_text}, where x is the device index.
    Devices are indexed based on the order of the COM ports specified by the -d option.
    The first device, {c_highlight}d[0]{c_text}, can also be accessed using {c_highlight}device{c_text}.

    Type {c_highlight}d[x].{c_text} and hit tab to see the available methods.
""" # NOQA: Ignore long line
#USAGE_STRING += colorama.Style.RESET_ALL

FILE_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
STREAM_LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
#COLOR_LIST = [colorama.Fore.MAGENTA, colorama.Fore.CYAN,
#              colorama.Fore.GREEN, colorama.Fore.YELLOW,
#              colorama.Fore.BLUE, colorama.Fore.RED]
#COLOR_INDEX = 0


def configure_logger(device_name):
    global options
    #global COLOR_INDEX

    logger = logging.getLogger(device_name)

    logger.setLevel(logging.DEBUG)

    stream_formatter = logging.Formatter(STREAM_LOG_FORMAT)
        #COLOR_LIST[COLOR_INDEX % len(COLOR_LIST)] + colorama.Style.BRIGHT
        #+ STREAM_LOG_FORMAT
        #+ colorama.Style.RESET_ALL
        #)
    #COLOR_INDEX = (COLOR_INDEX + 1) % len(COLOR_LIST)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(options.log_level)
    logger.addHandler(stream_handler)

    if not options.no_logfile:
        dt = DateTime.DateTime()
        logfile = "{}_{}-{}-{}-{}_output.log".format(
            device_name, dt.yy(), dt.dayOfYear(), dt.hour(), dt.minute())
        logfile = os.path.join(LOG_DIR, logfile)
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(FILE_LOG_FORMAT)
        fh.setFormatter(file_formatter)
        logger.addHandler(fh)
    return logger


class Interactive(object):
    DEFAULT_APP_KEY = bytearray([0xAA] * 16)
    DEFAULT_SUBNET_KEY = bytearray([0xBB] * 16)
    DEFAULT_VIRTUAL_ADDRESS = bytearray([0xCC] * 16)
    DEFAULT_STATIC_AUTH_DATA = bytearray([0xDD] * 16)
    DEFAULT_LOCAL_UNICAST_ADDRESS_START = 0x0001
    CONFIG = ApplicationConfig(
        header_path=os.path.join(os.path.dirname(sys.argv[0]),
                                 ("../../examples/serial/include/"
                                  + "nrf_mesh_config_app.h")))
    PRINT_ALL_EVENTS = True

    def __init__(self, acidev):
        self.acidev = acidev
        self._event_filter = []
        self._event_filter_enabled = True
        self._other_events = []

        self.logger = configure_logger(self.acidev.device_name)
        self.send = self.acidev.write_aci_cmd

        # Increment the local unicast address range
        # for the next Interactive instance
        self.local_unicast_address_start = (
            self.DEFAULT_LOCAL_UNICAST_ADDRESS_START)
        Interactive.DEFAULT_LOCAL_UNICAST_ADDRESS_START += (
            self.CONFIG.ACCESS_ELEMENT_COUNT)

        self.access = access.Access(self, self.local_unicast_address_start,
                                    self.CONFIG.ACCESS_ELEMENT_COUNT)
        self.model_add = self.access.model_add

        # Adding the packet recipient will start dynamic behavior.
        # We add it after all the member variables has been defined
        self.acidev.add_packet_recipient(self.__event_handler)


    def close(self):
        self.acidev.stop()

    def events_get(self):
        return self._other_events

    def event_filter_add(self, event_filter):
        self._event_filter += event_filter

    def event_filter_disable(self):
        self._event_filter_enabled = False

    def event_filter_enable(self):
        self._event_filter_enabled = True

    def device_port_get(self):
        return self.acidev.serial.port

    def quick_setup(self):
        self.send(cmd.SubnetAdd(0, bytearray(self.DEFAULT_SUBNET_KEY)))
        self.send(cmd.AppkeyAdd(0, 0, bytearray(self.DEFAULT_APP_KEY)))
        self.send(cmd.AddrLocalUnicastSet(
            self.local_unicast_address_start,
            self.CONFIG.ACCESS_ELEMENT_COUNT))

    def __event_handler(self, event):
        if self._event_filter_enabled and event._opcode in self._event_filter:
            # Ignore event
            return
        if event._opcode == evt.Event.DEVICE_STARTED:
            self.logger.info("Device rebooted.")

        elif event._opcode == evt.Event.CMD_RSP:
            if event._data["status"] != 0:
                self.logger.error("{}: {}".format(
                    cmd.response_deserialize(event),
                    STATUS_CODE_LUT[event._data["status"]]["code"]))
            else:
                text = str(cmd.response_deserialize(event))
                print(text)
                if text == "None":
                    text = "Success"
                self.logger.info(text)
        else:
            if self.PRINT_ALL_EVENTS and event is not None:
                self.logger.info(str(event))
                print(str(event))
            else:
                self._other_events.append(event)

class Commands(helloworld_pb2_grpc.GreeterServicer):

	def __init__(self, device):
		self.device = device
		print("Commands")

	def SayHello(self, request, context):
		print("%s" % request.name)
		gc = GenericOnOffClient()
		self.device.model_add(gc)
		gc.publish_set(0, 0)
		gc.set(True)
		return helloworld_pb2.HelloReply(message='Command, %s' % request.name)

	def SayHelloAgain(self, request, context):
		return helloworld_pb2.HelloReply(message='Commands more, %s' % request.name)

async def start_event_loop(options):
	#colorama.init()
	comports = options.devices
	d = list()

    # Print out a mini intro to the interactive session --
    # Start with white and then magenta to keep the session white
    # (workaround for a bug in ipython)
    #colors = {"c_default": colorama.Fore.WHITE + colorama.Style.BRIGHT,
    #          "c_highlight": colorama.Fore.YELLOW + colorama.Style.BRIGHT,
    #          "c_text": colorama.Fore.CYAN + colorama.Style.BRIGHT}

	#print(USAGE_STRING.format(**colors))
	if not options.no_logfile and not os.path.exists(LOG_DIR):
		print("Creating log directory: {}".format(os.path.abspath(LOG_DIR)))
		os.mkdir(LOG_DIR)

	for dev_com in comports:
		d.append(Interactive(Uart(port=dev_com,baudrate=options.baudrate, device_name=dev_com.split("/")[-1])))

	device = d[0]

	print(device)
    
	send = device.acidev.write_aci_cmd  # NOQA: Ignore unused variable

	# Set iPython configuration
	#ipython_config = traitlets.config.get_config()
	if options.no_logfile:
		print("no log file")
		#ipython_config.TerminalInteractiveShell.logstart = False
		#ipython_config.InteractiveShellApp.db_log_output = False
	else:
		dt = DateTime.DateTime()
		logfile = "{}/{}-{}-{}-{}_interactive_session.log".format(LOG_DIR, dt.yy(), dt.dayOfYear(), dt.hour(), dt.minute())

        #ipython_config.TerminalInteractiveShell.logstart = True
        #ipython_config.InteractiveShellApp.db_log_output = True
        #ipython_config.TerminalInteractiveShell.logfile = logfile

    #ipython_config.TerminalInteractiveShell.confirm_exit = False
    #ipython_config.InteractiveShellApp.multiline_history = True
    #ipython_config.InteractiveShellApp.log_level = logging.DEBUG

    #IPython.embed(config=ipython_config)
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	helloworld_pb2_grpc.add_GreeterServicer_to_server(Commands(device), server)
	server.add_insecure_port('[::]:50051')
	server.start()
	server.wait_for_termination()
	#with grpc.insecure_channel('localhost:50051') as channel:
	#	stub = helloworld_pb2_grpc.GreeterStub(channel)
	#	while True:
	# await asyncio.sleep(1)
	# response = stub.SayHello(helloworld_pb2.HelloRequest(name='world'))
	# print("Client received: " + response.message)

	for dev in d:
		dev.close()
	raise SystemExit(0)


if __name__ == '__main__':

	parser = ArgumentParser(
        description="nRF5 SDK for Mesh Event Loop PyACI")
	parser.add_argument("-d", "--device",
                        dest="devices",
                        nargs="+",
                        required=True,
                        help=("Device Communication port, e.g., COM216 or "
                              + "/dev/ttyACM0. You may connect to multiple "
                              + "devices. Separate devices by spaces, e.g., "
                              + "\"-d COM123 COM234\""))
	parser.add_argument("-b", "--baudrate",
                        dest="baudrate",
                        required=False,
                        default='115200',
                        help="Baud rate. Default: 115200")
	parser.add_argument("--no-logfile",
                        dest="no_logfile",
                        action="store_true",
                        required=False,
                        default=False,
                        help="Disables logging to file.")
	parser.add_argument("-l", "--log-level",
                        dest="log_level",
                        type=int,
                        required=False,
                        default=3,
                        help=("Set default logging level: " + "1=Errors only, 2=Warnings, 3=Info, 4=Debug"))
	
	options = parser.parse_args()

	if options.log_level == 1:
		options.log_level = logging.ERROR
	elif options.log_level == 2:
		options.log_level = logging.WARNING
	elif options.log_level == 3:
		options.log_level = logging.INFO
	else:
		options.log_level = logging.DEBUG

	loop = asyncio.get_event_loop()

	try:
		asyncio.ensure_future(start_event_loop(options))
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		print("Closing Loop")
		loop.close()
    