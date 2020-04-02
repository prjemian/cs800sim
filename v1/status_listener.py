#!/usr/bin/env python

"""
listen for status broadcasts on UDP
"""

import datetime
import logging
import socket
import time

import utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)

STATUS_PORT = 30304
STATUS_HOST = ""
STATUS_IDS = utils.getStatusIds()
REVERSE_IDS = {v:k for k, v in STATUS_IDS.items()}


def get_status(sock):
    data, addr = sock.recvfrom(1024)
    t = time.time()
    dt = datetime.datetime.fromtimestamp(t)
    iso = dt.isoformat(sep=" ", timespec="milliseconds")
    ip, port = addr

    # * HEADER_BYTE1, HEADER_BYTE2 – unique 16-bit header 
    # * DATA_SIZE_BYTE1, DATA_SIZE_BYTE2 – data size in bytes (16 bit);   
    # * ID_BYTE1, ID_BYTE2 – 16 bit Param Id 
    # * VALUE_BYTE1, VALUE_BYTE2, ... – 16 bit Param Value 
    # * CHECKSUM_BYTE1, CHECKSUM_BYTE2 – 16-bit checksum calculated 
    #     as simple 16-bit sum of all the ids and values 
    # * FOOTER _BYTE1, FOOTER _BYTE2 – unique 16-bit footer 

    # The HEADER is defined as 0xAAAB and the FOOTER is defined as 0xABAA.
    data_size = utils.bs2i(data[2:4])
    # TODO: multiple ParamIDs are sent together
    # TODO: all data values are 16-bit integers
    parm = REVERSE_IDS[data[4:6]]
    values = data[6:6+data_size]
    if data_size <= 6:
        values = utils.bs2i(values)
    if parm.endswith("Temp"):
        values = values/100.0

    return dict(
        time=t,
        iso8601=iso,
        ip=ip,
        port=port,
        data=data,
        data_size=data_size,
        statusID=parm,
        value=values,
    )


def listen_for_status(host=STATUS_HOST):
    """
    listen for the UDP status broadcasts of the CS800 controller(s)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable broadcasting mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((host, STATUS_PORT))

    logger.info("Status updates from %s on port %d", host, STATUS_PORT)

    while True:
        status = get_status(sock)
        print(status)


if __name__ == "__main__":
    listen_for_status()
