#!/usr/bin/env python

"""
emit ID message
"""

import logging
import socket
import time

import utils


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


def announcer():
    """
    announce our NetBIOS name and MAC address by UDP broadcasts every second
    """
    udp_port = 30303			        # CS800 ID broadcast port
    udp_host = "<broadcast>"            # always broadcast
    mac_addr = utils.get_mac()[0]       # MAC as string
    netbios_name = socket.gethostname().split(".")[0]

    # is MAC address coded as text or binary?
    # length of actual message received will be informative
    msg = "{:16s}".format(netbios_name).encode()
    imac = int("0x" + mac_addr, 0)   # base=0: interpret exactly as a code literal
    msg += utils.i2bs(imac)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # For linux hosts all sockets that want to share the same address
    # and port combination must belong to processes that share the same
    # effective user ID!

    # Enable broadcasting mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    sock.settimeout(0.2)

    logger.info("%s (MAC: %s)", netbios_name, mac_addr)

    t0 = time.time()

    while True:
        if time.time() > t0:
            sock.sendto(msg, (udp_host, udp_port))
            logger.debug("message sent: %s", msg)
            t0 += 1
        time.sleep(0.01)


if __name__ == "__main__":
    announcer()
