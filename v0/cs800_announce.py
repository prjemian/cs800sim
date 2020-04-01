#!/usr/bin/python

"""
mimic the CS800 broadcast on port 30303

The 800 Series Oxford Cryosystems controller broadcast its
IP address, NetBIOS name and MAC address on port 30303.
This information is sent as a UDP packet. The IP address
is obtained from the properties of the UDP packet whereas
the NetBIOS name and MAC address is sent in the packet
data section. The first 16 bytes of the data section
contains the NetBIOS name and the subsequent bytes contain
the MAC address of the controller.

Note: Port 30303 should be opened in the firewall.
"""

import socket
import time
import uuid

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      # For UDP

udp_host = socket.gethostname()		# Host IP
udp_port = 30303			        # specified port to connect
node = uuid.getnode()
mac_addr = hex(uuid.getnode())      # MAC address

netbios_name = udp_host.split(".")[0]
mac_addr = mac_addr[2:].rstrip("L")

# is MAC address coded as text or binary?
# length of actual message received will be informative
msg = "{:16s}{}".format(netbios_name, mac_addr).encode()

# broadcast to local subnet
udp_host = "192.168.144.99"

print("UDP target IP:", udp_host)
print("UDP target Port:", udp_port)

print("msg=|{}|".format(msg))
print("    |{}|".format("1234567890"*4))

for i in range(5):
    # Sending message to UDP server
    sock.sendto(msg,(udp_host, udp_port))
    time.sleep(1.0)
