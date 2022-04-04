from mesh.access import Model, Opcode

from models.common import TransitionTime

import struct


class GenericOnOffClient(Model):
    GENERIC_ON_OFF_SET = Opcode(0x8202, None, "Generic OnOff Set")
    GENERIC_ON_OFF_SET_UNACKNOWLEDGED = Opcode(0x8203, None, "Generic OnOff Set Unacknowledged")
    GENERIC_ON_OFF_GET = Opcode(0x8201, None, "Generic OnOff Get")
    GENERIC_ON_OFF_STATUS = Opcode(0x8204, None, "Generic OnOff Status")

    def __init__(self):
        self.opcodes = [
            (self.GENERIC_ON_OFF_STATUS, self.__generic_on_off_status_handler)]
        self.__tid = 0
        super(GenericOnOffClient, self).__init__(self.opcodes)

    def set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<BB", int(value > 0), self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            self.send(self.GENERIC_ON_OFF_SET, message)
        else:
            self.send(self.GENERIC_ON_OFF_SET_UNACKNOWLEDGED, message)

    def get(self):
        self.send(self.GENERIC_ON_OFF_GET)

    @property
    def _tid(self):
        tid = self.__tid
        self.__tid += 1
        if self.__tid >= 255:
            self.__tid = 0
        return tid

    def __generic_on_off_status_handler(self, opcode, message):
        logstr = "Present OnOff: " + "on" if message.data[0] > 0 else "off"
        if len(message.data) > 1:
            logstr += " Target OnOff: " + "on" if message.data[1] > 0 else "off"

        if len(message.data) == 3:
            logstr += " Remaining time: %d ms" % (TransitionTime.decode(message.data[2]))

        self.logger.info(logstr)
