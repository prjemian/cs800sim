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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)


class CS800:
    """
    simulate the CS800 controller
    """

    def __init__(self):
        self.status_ids = utils.getStatusIds()

        self.udp_port = 30304			        # CS800 status broadcast port
        self.udp_host = "<broadcast>"            # always broadcast
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.2)

        self.status_keys = ["StatusGasTemp",]
        self.offset_temperature = 2.5   # add realism to simulator
        self.controller_memory = {
            "DeviceType" : "CS800 controller",  # correct data type?

            # simulate some values
            "StatusGasTemp" : 100.0,
            "StatusGasSetPoint" : 100.0,
        }
        self.readGasTemp()
    
    def readGasTemp(self):
        "simulate"
        sp = self.controller_memory["StatusGasSetPoint"]
        value = sp + self.offset_temperature + 1.5*np.random.standard_normal()
        self.controller_memory["StatusGasTemp"] = value
        self.controller_memory["time"] = time.time()
        return value
    
    def create_message(self, paramID):
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
        data_values = bytes(4)

        param_id_bs = self.status_ids[paramID]
        value = self.controller_memory[paramID]
        if paramID in ("StatusGasTemp", "StatusGasSetPoint"):
            value = int(value*100 + 0.5)    # report T in centiKelvin
            data_values = utils.i2bs(value)

        def convert(n):     # ensure output is 2 bytes long
            if n > 255:
                return utils.i2bs(n)
            else:
                return bytes((0, n))
        data_size = convert(len(data_values))
        cksum = convert(sum([c for c in param_id_bs + data_values]) % 65536)

        msg = header + data_size + param_id_bs + data_values + cksum + footer
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
            for parm in self.status_keys:
                msg = self.create_message(parm)
                logger.debug("%s = %s : msg = %s", parm, str(self.controller_memory[parm]), msg)
                self.sock.sendto(msg, (self.udp_host, self.udp_port))
            time.sleep(1)


if __name__ == "__main__":
    cs800 = CS800()
    cs800.emit_status()
