#!/usr/bin/python

"""
discover any CS800 controllers on the LAN

The CS800 controllers broadcast their NetBIOS name
and MAC address by UDP to port 30303 every second.

With this program running, any CS800 controllers on the 
subnet will be reported.

The 800 Series Oxford Cryosystems controller broadcast its
IP address, NetBIOS name and MAC address on port 30303.
This information is sent as a UDP packet. The IP address
is obtained from the properties of the UDP packet whereas
the NetBIOS name and MAC address is sent in the packet
data section. The first 16 bytes of the data section
contains the NetBIOS name and the subsequent bytes contain
the MAC address of the controller.
"""

import datetime
import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
udp_host = socket.gethostname()		    # Host IP
udp_port = 30303			            # CS800 broadcast port

sock.bind((udp_host,udp_port))
t0 = time.time()

print("Waiting for CS800 controllers to announce themselves...")

while True:
    data, addr = sock.recvfrom(1024)    # receive UDP data
    t = time.time()
    dt = datetime.datetime.fromtimestamp(t).isoformat(sep=" ")
    ip, port = addr
    netbios_name = data[:16].strip()
    mac_addr = data[16:]
    print(
        "({}, {:.3f}, {}:{}) {} {}".format(
            dt, t-t0, ip, port, netbios_name, mac_addr))
