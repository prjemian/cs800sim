#!/usr/bin/python

# see: https://www.studytonight.com/network-programming-in-python/working-with-udp-sockets

import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

udp_host = socket.gethostname()		# Host IP
udp_port = 12345			        # specified port to connect
udp_host = "otz.xray.aps.anl.gov"

msg = "Hello Python!"
print("UDP target IP:", udp_host)
print("UDP target Port:", udp_port)

sock.sendto(msg,(udp_host, udp_port))		# Sending message to UDP server
