
from mesh.access import Model, Opcode

from models.common import TransitionTime

import struct

import warnings

class GenericLevelClient(Model):
    GENERIC_LEVEL_GET = Opcode(0x8205, None, "Generic Level Get")
    GENERIC_LEVEL_SET = Opcode(0x8206, None, "Generic Level Set")
    GENERIC_LEVEL_SET_UNACKNOWLEDGED = Opcode(0x8207, None, "Generic Level Set Unacknowledged")
    GENERIC_LEVEL_STATUS = Opcode(0x8208, None, "Generic Level Status")
    GENERIC_LEVEL_DELTA_SET = Opcode(0x8209, None, "Generic Level Delta Set")
    GENERIC_LEVEL_DELTA_SET_UNACKNOWLEDGED = Opcode(0x820A, None, "Generic Level Delta Set Unacknowledged")
    GENERIC_LEVEL_MOVE_SET = Opcode(0x820B, None, "Generic Level Move Set")
    GENERIC_LEVEL_MOVE_SET_UNACKNOWLEDGED = Opcode(0x820C, None, "Generic Level Move Set Unacknowledged")
    MIN_VALUE = -65536
    MAX_VALUE = 65536

    def __init__(self):
        self.opcodes = [
            (self.GENERIC_LEVEL_STATUS, self.__generic_level_status_handler)]

        self.__tid = 0

        super(GenericLevelClient, self).__init__(self.opcodes)

    def set(self, value, transition_time_ms=0, delay_ms=0, ack=True):

        self.logger.info("SET")

        message = bytearray()
        
        if (value < self.MIN_VALUE or value > self.MAX_VALUE):
            warnings.warn("Generic level value must be between -65536 and 65536")
        else:
            message += struct.pack("<iI", int(value), self._tid)

            if transition_time_ms > 0:
                message += TransitionTime.pack(transition_time_ms, delay_ms)

            if ack:
                self.send(self.GENERIC_LEVEL_SET, message)

                self.logger.info("ACK")

                print(self.GENERIC_LEVEL_SET, message)

                self.logger.info(message)

                self.logger.info(self.GENERIC_LEVEL_SET)

            else:
                self.send(self.GENERIC_LEVEL_SET_UNACKNOWLEDGED, message)

                print(self.GENERIC_LEVEL_SET_UNACKNOWLEDGED, message)

                self.logger.info(message)

                self.logger.info(self.GENERIC_LEVEL_SET_UNACKNOWLEDGED)

    def get(self):
        self.send(self.GENERIC_LEVEL_GET)

    def delta(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<iI", int(value), self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            self.send(self.GENERIC_LEVEL_DELTA_SET, message)
        else:
            self.send(self.GENERIC_LEVEL_DELTA_SET_UNACKNOWLEDGED, message)

    def move(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<iI", int(value), self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            self.send(self.GENERIC_LEVEL_MOVE_SET, message)
        else:
            self.send(self.GENERIC_LEVEL_MOVE_SET_UNACKNOWLEDGED, message)

    @property
    def _tid(self):
        tid = self.__tid
        self.__tid += 1
        if self.__tid >= 255:
            self.__tid = 0
        return tid

    def __generic_level_status_handler(self, opcode, message):
        logstr = "Present OnOff: " + "on" if message.data[0] > 0 else "off"
        if len(message.data) > 1:
            logstr += " Target OnOff: " + "on" if message.data[1] > 0 else "off"

        if len(message.data) == 3:
            logstr += " Remaining time: %d ms" % (TransitionTime.decode(message.data[2]))

        self.logger.info(logstr)
