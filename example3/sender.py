#!/usr/bin/env python

"""
sender

see: https://github.com/ninedraft/python-udp/blob/master/server.py
"""

import socket
import time
import uuid

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
# Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
# For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
# So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
# Thanks to @stevenreddie
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

# Enable broadcasting mode
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Set a timeout so the socket does not block
# indefinitely when trying to receive data.
sock.settimeout(0.2)
message = b"your very important message"
while True:
    msg = str(uuid.uuid4()).split("-")[0].encode()
    sock.sendto(msg, ("<broadcast>", 37020))
    print("message sent!")
    time.sleep(1)
