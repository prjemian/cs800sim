#!/usr/bin/env python

"""
emit ID message
"""

import logging
import socket
import time
import uuid

import utils


logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)


def announcer():
    """
    announce our NetBIOS name and MAC address by UDP broadcasts every second
    """
    udp_port = 30303			        # CS800 ID broadcast port
    udp_host = "<broadcast>"            # always broadcast
    mac_addr = uuid.getnode()           # MAC as integer
    netbios_name = socket.gethostname().split(".")[0]

    # is MAC address coded as text or binary?
    # length of actual message received will be informative
    msg = "{:16s}".format(netbios_name).encode()
    msg += utils.i2bs(mac_addr)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # For linux hosts all sockets that want to share the same address
    # and port combination must belong to processes that share the same
    # effective user ID!

    # Enable broadcasting mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    sock.settimeout(0.2)

    t0 = time.time()

    while True:
        if time.time() > t0:
            sock.sendto(msg, (udp_host, udp_port))
            logger.debug("message sent!")
            t0 += 1
        time.sleep(0.02)


if __name__ == "__main__":
    announcer()
