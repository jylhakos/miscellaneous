
from mesh.access import Model, Opcode

from models.common import TransitionTime

import struct

import warnings

class CTL(Model):
    CTL_SET_ACK = Opcode(0x8264, None, "CTL Set")
    CTL_SET_UNACK = Opcode(0x8265, None, "CTL Set Unacknowledged")

    MIN_VALUE = -65536
    MAX_VALUE = 65536

    def __init__(self):
        self.opcodes = []

        self.__tid = 0

        super(CTL, self).__init__(self.opcodes)

    def set(self, value_tmp, value_duv, transition_time_ms=0, delay_ms=0, ack=False):

        self.logger.info("SET")

        message = bytearray()
        
        if (value_tmp < self.MIN_VALUE or value_tmp > self.MAX_VALUE):
            warnings.warn("CTL value must be between -65536 and 65536")

        message += struct.pack("<iiI", int(value_tmp), int(value_duv), self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
                self.send(self.CTL_SET_ACK, message)

                print(self.CTL_SET_ACK, message)

                self.logger.info(message)

                self.logger.info(self.CTL_SET_ACK)
        else:
                self.send(self.CTL_SET_UNACK, message)

                print(self.CTL_SET_UNACK, message)

                self.logger.info(message)

                self.logger.info(self.CTL_SET_UNACK)

    @property
    def _tid(self):
        tid = self.__tid
        self.__tid += 1
        if self.__tid >= 255:
            self.__tid = 0
        return tid
