#!/usr/bin/env python

"""
simulate a CS8000 controller that receives commands (replies are not in the spec)

Sending a command requires a UDP socket to be created using the 
controller's IP address and the command port 30305.

If the command is unrecognised (Id invalid or Size inappropriate), 
illegal (parameter out of range) or inappropriate (e.g. the 
machine has shutdown), then it is simply ignored.
"""

import datetime
import logging
import socket
import time

import utils

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)

COMMAND_PORT = 30305
COMMAND_HOST = ""
REVERSE_IDS = {v:k for k, v in utils.COMMAND_IDS.items()}


class CS800controller:
    """
    simulate a CS8000 controller that receives commands (replies are not in the spec)
    """

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # Enable broadcasting mode
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind((COMMAND_HOST, COMMAND_PORT))

        logger.info("Commands from '%s' on port %d", COMMAND_HOST, COMMAND_PORT)

    def handler(self, callback=None):
        """
        handle CS800 commands from UDP
        """
        while True:
            data, addr = self.sock.recvfrom(1024)
            t = time.time()
            dt = datetime.datetime.fromtimestamp(t)
            iso = dt.isoformat(sep=" ", timespec="milliseconds")
            ip, port = addr

            # confirm the checksum or report CHECKSUM_ERROR
            reported_cksum = utils.bs2i(data[6])
            calc_cksum = utils.checksum(data[:6], 1)
            if calc_cksum != reported_cksum:
                logger.error("Command checksum error")
                return dict(
                    time=t,
                    datetime=iso,
                    ip=ip,
                    port=port,
                    error="checksum error"
                    )

            # COMMAND_ID (high byte), COMMAND_ID (low byte)
            # PARAM1 (high byte), PARAM1 (low byte)
            # PARAM2 (high byte), PARAM2 (low byte)
            # CHECKSUM_BYTE - an 8-bit sum of bytes. 
            command_id = REVERSE_IDS[data[0:2]]
            arg1 = utils.bs2i(data[2:4])
            arg2 = utils.bs2i(data[4:2])

            command_data = dict(
                time=t,
                datetime=iso,
                ip=ip,
                port=port,
                # data=data,
                command_id=command_id,
                arg1=arg1,
                arg2=arg2,
            )
            logger.debug("command: %s", str(command_data))
            if callback is not None:
                callback(command_data)


def command_handler():
    """
    handle CS800 commands received via UDP
    """
    cs800 = CS800controller()
    cs800.handler()


if __name__ == "__main__":
    command_handler()
