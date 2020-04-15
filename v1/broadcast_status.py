#!/usr/bin/env python

"""
emit status of CS800 controller via UDP broadcast
"""

import json
import logging
import numpy as np
import os
import socket
import time

import utils

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def rand(base, width):
    return base + width*np.random.random()


def rand_norm(base, width):
    return base + width*np.random.standard_normal()


class CS800:
    """
    simulate the CS800 controller
    """

    constant_parameters = """
        StatusGasTemp StatusGasSetPoint
        StatusRunMode StatusPhaseId
        SetUpControllerNumber
        SetUpCommissionDate
        SetUpColdheadNumber
        DeviceH8Firmware
        StatusRampRate
        StatusTargetTemp
        StatusRemaining
        StatusRunTime
        """.split()

    def __init__(self):
        self.udp_port = 30304			        # CS800 status broadcast port
        self.udp_host = "255.255.255.255"        # or "<broadcast>"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.2)

        self.status_keys = utils.EPICS_PARAMETERS
        # self.offset_temperature = 2.5   # add realism to simulator
        self.smoothing = 0.90   # 0 .. 1 : higher is slower to converge
        self.noise_amplitude = 0.1       # RMS fluctuations, K

        # set some initial values, not typical though
        self.memory = {k: utils.bs2i(v) for k, v in utils.STATUS_IDS.items()}
        self.memory["StatusGasSetPoint"] = 100.0
        self.memory["StatusGasTemp"] = 100.0
        self.memory["StatusTargetTemp"] = 100.0
        self.memory["StatusRunTime"] = 0.0
        self.start_time = time.time()

        self.run_mode = "Startup"
        self.phase_id = "Hold"
        self.memory["StatusRunMode"] = self.run_mode
        self.memory["StatusPhaseId"] = self.phase_id
        self.memory["StatusRampRate"] = 360

        self.memory["SetUpControllerNumber"] = int(rand(3100, 30))
        self.memory["SetUpColdheadNumber"] = int(rand(3220, 30))
        self.memory["SetUpCommissionDate"] = int(rand(3330, 30))
        self.memory["DeviceH8Firmware"] = int(rand(1100, 30))

        self.readGasTemp()

    @property
    def phase_id(self):
        return utils.PHASE_IDS.index(self._phase_id)

    @phase_id.setter
    def phase_id(self, phase):
        if phase in utils.PHASE_IDS:
            # set by text
            self._phase_id = phase
            self.memory["StatusPhaseId"] = self.phase_id
        elif isinstance(phase, int) and 0 <= phase < len(utils.PHASE_IDS):
            # set by index
            self._phase_id = utils.PHASE_IDS[phase]
            self.memory["StatusPhaseId"] = self.phase_id

    @property
    def run_mode(self):
        return utils.RUN_MODES.index(self._run_mode)

    @run_mode.setter
    def run_mode(self, text):
        if text in utils.RUN_MODES:
            self._run_mode = text
            self.memory["StatusRunMode"] = self.run_mode

    def readGasTemp(self):
        "simulated temperatures"
        sp = self.memory["StatusGasSetPoint"]
        sp = max(80, min(300, sp))
        old = self.memory["StatusGasTemp"]
        old = max(80, min(300, old))
        eta = self.smoothing
        value = eta*sp + (1 - eta)*old
        noise = rand_norm(0, self.noise_amplitude)
        self.memory["StatusGasTemp"] = value + noise
        self.memory["StatusRunTime"] = (time.time() - self.start_time)/60.0

        self.memory["time"] = time.time()
        for parm in utils.STATUS_IDS.keys():
            if parm not in self.constant_parameters:
                if parm in utils.TEMPERATURE_PARAMETERS:
                        self.memory[parm] = rand_norm(150, 5)
                elif parm in utils.PERCENT_PARAMETERS:
                        self.memory[parm] = rand_norm(30, 5)
                else:
                    self.memory[parm] = rand_norm(500, 50)
        return value
    
    def create_message(self):
        """
        format the message to be sent

        The data section of a UDP status packets has the following structure: 

        HEADER_BYTE1, HEADER_BYTE2, DATA_SIZE_BYTE1, DATA_SIZE_BYTE2, ID_BYTE1, ID_BYTE2,
        VALUE_BYTE1, VALUE_BYTE2, …, CHECKSUM_BYTE1, CHECKSUM_BYTE2, FOOTER_BYTE1,
        FOOTER_BYTE2 

        * HEADER_BYTE1, HEADER_BYTE2 – unique 16-bit header 
        * DATA_SIZE_BYTE1, DATA_SIZE_BYTE2 – data size in bytes (16 bit);   
        * ID_BYTE1, ID_BYTE2 – 16 bit Param Id 
        * VALUE_BYTE1, VALUE_BYTE2, ... – 16 bit Param Value 
        * CHECKSUM_BYTE1, CHECKSUM_BYTE2 – 16-bit checksum calculated 
          as simple 16-bit sum of all the ids and values 
        * FOOTER _BYTE1, FOOTER _BYTE2 – unique 16-bit footer 

        The HEADER is defined as 0xAAAB and the FOOTER is defined as 0xABAA.
        """

        header = bytes((0xaa, 0xab))
        footer = bytes((0xab, 0xaa))

        data = b""
        for parm in utils.STATUS_IDS.keys():
            parm_id = utils.STATUS_IDS[parm]
            value = self.memory[parm]
            if parm in utils.TEMPERATURE_PARAMETERS:
                value = int(value*100 + 0.5)    # report T in centiKelvin
            data += parm_id + utils.encode2bytes(int(value))
            # ll = len(data)
            # logger.debug("%d ParamID=%s: msg=%s", ll, parm, parm_id + utils.encode2bytes(value))

        data_size = utils.encode2bytes(len(data))
        cksum = utils.encode2bytes(utils.checksum(data, 2))

        msg = header + data_size + data + cksum + footer
        logger.debug("status message: %s", msg)
        return msg

    def emit_status(self):
        """
        send the status of this controller

        Only send the values from `self.status_keys`, not everything
        since this is configurable on the controller.
        """
        while True:
            self.readGasTemp()
            # print(self.memory)
            msg = self.create_message()
            logger.debug("msg = %s", msg)
            self.sock.sendto(msg, (self.udp_host, self.udp_port))
            time.sleep(1)


if __name__ == "__main__":
    cs800 = CS800()
    cs800.emit_status()
