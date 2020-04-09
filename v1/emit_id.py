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
    
    Broadcast consists of two parts: Netbios name and MAC address.
    The documentation states:
    
        The IP address is obtained from the properties of the UDP 
        packet whereas the NetBIOS name and MAC address is sent in 
        the packet data section. The first 16 bytes of the data 
        section contains the NetBIOS name and the subsequent bytes 
        contain the MAC address of the controller. 

    This packet dump from a CS800 controller is different:
    
        ffff ffff ffff ffff ffff ffff ffff ff0d
        0a30 302d 3030 2d30 432d 3031 2d30 312d 4142
    
    or 
    
        0xff*15 + CR + LF + "00-00-0C-01-01-AB"
    
    where the last 17 bytes are the controller's MAC address in text.
    In this case, it must be that the controller has no assigned
    Netbios name, thus the series of 0xff bytes.
    """
    udp_port = 30303			        # CS800 ID broadcast port
    udp_host = "<broadcast>"            # or "<broadcast>"
    mac_addr = utils.get_mac()[0]       # MAC as string
    netbios_name = socket.gethostname().split(".")[0]

    # MAC address is coded as text 
    bsmac = "-".join([mac_addr[p:p+2] for p in range(0, len(mac_addr), 2)])

    msg = "{:15s}".format(netbios_name).encode()
    msg += bytes((0x0d, 0x0a))
    msg += bsmac.encode()

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
