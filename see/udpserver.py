#!/usr/bin/python

# see: https://www.studytonight.com/network-programming-in-python/working-with-udp-sockets

import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

udp_host = socket.gethostname()		        # Host IP
udp_port = 12345			                # specified port to connect

sock.bind((udp_host,udp_port))

print("UDP server IP:", udp_host)
print("UDP server Port:", udp_port)

while True:
	print("Waiting for client...")
	data,addr = sock.recvfrom(1024)	        #receive data from client
	print("Received Messages:",data," from",addr)
