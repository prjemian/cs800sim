#!/usr/bin/env python

"""
discover CS800 controllers by their UDP broadcasts
"""

import datetime
import logging
import socket
import time
import uuid

import utils


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def discover():
    """
    listen for CS800 identity UDP broadcasts
    """
    udp_port = 30303			        # CS800 ID broadcast port
    udp_host = ""                       # nothing in particular

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # For linux hosts all sockets that want to share the same address
    # and port combination must belong to processes that share the same
    # effective user ID!

    # Enable broadcasting mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.bind((udp_host, udp_port))
    logger.info("Listening for CS800 ID on port: %d", udp_port)

    while True:
        data, addr = sock.recvfrom(1024)
        t = time.time()
        dt = datetime.datetime.fromtimestamp(t).isoformat(sep=" ", timespec="milliseconds")
        ip, port = addr
        if len(data) == 22:
            netbios_name = data[:16].decode().strip()
            mac_addr = hex(utils.bs2i(data[16:])).lstrip("0x")
            print(
                "({},{}:{}) {} {}".format(
                    dt,
                    ip,
                    port,
                    netbios_name,
                    mac_addr
                    )
                )
        else:
            print("({}, {} {}) {}".format(dt, ip, len(data), data))


if __name__ == "__main__":
    discover()
