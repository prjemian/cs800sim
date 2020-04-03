#!/usr/bin/env python

"""
send commands to a specific (by IP) CS800 controller

Sending a command requires a UDP socket to be created using the 
controller's IP address and the command port 30305.

NOTE: The CS800 will not reply.
"""

import datetime
import logging
import socket
import time

import utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)

COMMAND_PORT = 30305
REVERSE_IDS = {v:k for k, v in utils.COMMAND_IDS.items()}


class CS800controller:
    """
    send commands to a CS8000 controller (replies are not in the spec)
    """

    def __init__(self, cs800_host):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # # Enable broadcasting mode
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.host = cs800_host
        # self.sock.bind((cs800_host, COMMAND_PORT))

        logger.info("Send commands to '%s' on port %d", cs800_host, COMMAND_PORT)

    def send_command(self, command, arg1=0, arg2=0):
        """
        send CS800 command via UDP
        """
        # COMMAND_ID (high byte), COMMAND_ID (low byte)
        # PARAM1 (high byte), PARAM1 (low byte)
        # PARAM2 (high byte), PARAM2 (low byte)
        # CHECKSUM_BYTE - an 8-bit sum of bytes. 
        command_id = utils.COMMAND_IDS[command.upper()]
        msg = command_id + utils.encode2bytes(arg1) + utils.encode2bytes(arg2)
        msg += utils.i2bs(utils.checksum(msg))
        logger.debug("sending %s(%d,%d): msg=%s", command, arg1, arg2, msg)
        self.sock.sendto(msg, (self.host, COMMAND_PORT))


def command_handler(host):
    """
    handle CS800 commands received via UDP
    """
    # RESTART=10,         # Restart a Cryostream which has shutdown
    # RAMP=11,            # Ramp command identifier - parameters follow
    # PLAT=12,            # Plat command identifier - parameter follows
    # HOLD=13,            # Hold command identifier - enter programmed Hold
    # COOL=14,            # Cool command identifier - parameter follows
    # END=15,             # End command identifier - parameter follows 
    # PURGE=16,           # Purge command identifier
    # PAUSE=17,           # Pause command identifier - enter temporary Hold
    # RESUME=18,          # Resume command identifier - exit temporary Hold 
    # STOP=19,            # Stop command identifier
    # TURBO=20,           # Turbo command identifier - parameter follows
    # SETSTATUSFORMAT=40, # Set status packet format - parameter follows 
    cs800 = CS800controller(host)
    cs800.send_command("restart")
    cs800.send_command("turbo", utils.TURBO_ON)
    cs800.send_command("ramp", 1, 80*100)
    cs800.send_command("plat", 2)
    cs800.send_command("cool", 40*100)
    cs800.send_command("end", 360)
    cs800.send_command("turbo", utils.TURBO_OFF)
    cs800.send_command("purge")
    cs800.send_command("pause")
    cs800.send_command("resume")
    cs800.send_command("stop")


if __name__ == "__main__":
    for ip in "192.168.144.99 192.168.144.113".split():
        logger.info("Sending command set to %s", ip)
        command_handler(ip)
