#!/usr/bin/env python

"""
listen for status broadcasts on UDP
"""

import argparse
import datetime
import logging
import pprint
import socket
import sys
import time

import utils

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

STATUS_PORT = 30304
STATUS_HOST = ""
REVERSE_IDS = {v:k for k, v in utils.STATUS_IDS.items()}


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

    # TODO: confirm the checksum or report CHECKSUM_ERROR

    base = 4
    status = {}
    for offset in range(0, data_size, 4):
        parm = REVERSE_IDS[data[base+offset:base+offset+2]]
        value = utils.bs2i(data[base+2+offset:base+2+offset+2])
        if parm in utils.TEMPERATURE_PARAMETERS:
            value = value/100.0     # T communicated in centiKelvin
        status[parm] = value

    return dict(
        time=t,
        datetime=iso,
        ip=ip,
        port=port,
        # data=data,
        data_size=data_size,
        status=status,
    )


def get_user_parameters():
    """configure user's command line parameters from sys.argv"""
    parser = argparse.ArgumentParser(
        prog='cs800', 
        description="listen to status broadcasts from CS800 controllers on the LAN")
    parser.add_argument(
        '--full',
        type=bool,
        default=False,
        help="full report (default: terse)")
    return parser.parse_args()


def listen_for_status():
    """
    listen for the UDP status broadcasts of the CS800 controller(s)
    """
    user_parms = get_user_parameters()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # Enable broadcasting mode
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((STATUS_HOST, STATUS_PORT))

    logger.info("Status updates from '%s' on port %d", STATUS_HOST, STATUS_PORT)

    while True:
        status = get_status(sock)
        if user_parms.full:
            pprint.pprint(status)
        else:
            # terse report
            print(
                f"({status['datetime']}"
                f",{status['ip']}"
                f",#{status['status']['SetUpControllerNumber']})"
                f" mode={status['status']['StatusRunMode']}"
                f" phase={status['status']['StatusPhaseId']}"
                f" SP={status['status']['StatusGasSetPoint']}"
                f" T={status['status']['StatusGasTemp']}"
            )
        sys.stdout.flush()


if __name__ == "__main__":
    listen_for_status()
