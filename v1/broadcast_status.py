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


class CS800:
    """
    simulate the CS800 controller
    """

    def __init__(self):
        self.udp_port = 30304			        # CS800 status broadcast port
        self.udp_host = "<broadcast>"            # always broadcast
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.2)

        self.status_keys = utils.EPICS_PARAMETERS
        self.offset_temperature = 2.5   # add realism to simulator

        # set some initial values, not typical though
        self.controller_memory = {k: utils.bs2i(v) for k, v in utils.STATUS_IDS.items()}
        self.controller_memory["StatusGasSetPoint"] = 100.0
        self.readGasTemp()
    
    def readGasTemp(self):
        "simulated temperatures"
        sp = self.controller_memory["StatusGasSetPoint"]
        value = sp + self.offset_temperature + 1.5*np.random.standard_normal()
        self.controller_memory["StatusGasTemp"] = value
        self.controller_memory["time"] = time.time()
        for parm in utils.STATUS_IDS.keys():
            if parm in utils.TEMPERATURE_PARAMETERS:
                if parm not in "StatusGasTemp StatusGasSetPoint".split():
                    self.controller_memory[parm] = 150 + 5*np.random.standard_normal()
            else:
                self.controller_memory[parm] = int(300 + 500*np.random.random())
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
            value = self.controller_memory[parm]
            if parm in utils.TEMPERATURE_PARAMETERS:
                value = int(value*100 + 0.5)    # report T in centiKelvin
            data += parm_id + utils.encode2bytes(value)
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
            # print(self.controller_memory)
            msg = self.create_message()
            logger.debug("msg = %s", msg)
            self.sock.sendto(msg, (self.udp_host, self.udp_port))
            time.sleep(1)


if __name__ == "__main__":
    cs800 = CS800()
    cs800.emit_status()
