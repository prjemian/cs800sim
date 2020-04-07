#!/usr/bin/env python

"""
utilities
"""

import collections
import json
import os
import psutil
import socket


TEMPERATURE_PARAMETERS = """
StatusGasTemp StatusGasSetPoint
DeviceMaxTemp
DeviceMinTemp
StatusColdheadTemp
StatusCollarTemp
StatusCryostatTemp
StatusEvapTemp
StatusNozzleSetTemp
StatusNozzleTemp
StatusSampleHolderTemp
StatusShieldTemp
StatusSuctSetTemp
StatusSuctTemp
StatusTargetTemp
""".split()

EPICS_PARAMETERS = """
AutoFillLNLevel
DeviceH8Firmware
DeviceMaxTemp
DeviceMinTemp
DeviceSubType
DeviceType
SetUpDefaultEvapAdjust
StatusAlarmCode
StatusAveSuctHeat
StatusColdheadHeat
StatusColdheadTemp
StatusCollarTemp
StatusCryostatTemp
StatusElapsed
StatusEvapAdjust
StatusEvapHeat
StatusEvapTemp
StatusGasError
StatusGasFlow
StatusGasHeat
StatusGasSetPoint
StatusGasTemp
StatusLinePressure
StatusNozzleHeat
StatusNozzleSetTemp
StatusNozzleTemp
StatusPhaseId
StatusRampRate
StatusRemaining
StatusRunMode
StatusRunTime
StatusSampleHeat
StatusSampleHolderPresent
StatusSampleHolderTemp
StatusShieldHeat
StatusShieldTemp
StatusSuctSetTemp
StatusSuctTemp
StatusTargetTemp
StatusTurboMode
StatusVacuumGauge
StatusVacuumSensor
""".split()

COMMAND_IDS = dict(
    RESTART=10,         # Restart a Cryostream which has shutdown
    RAMP=11,            # Ramp command identifier - parameters follow
    PLAT=12,            # Plat command identifier - parameter follows
    HOLD=13,            # Hold command identifier - enter programmed Hold
    COOL=14,            # Cool command identifier - parameter follows
    END=15,             # End command identifier - parameter follows 
    PURGE=16,           # Purge command identifier
    PAUSE=17,           # Pause command identifier - enter temporary Hold
    RESUME=18,          # Resume command identifier - exit temporary Hold 
    STOP=19,            # Stop command identifier
    TURBO=20,           # Turbo command identifier - parameter follows
    SETSTATUSFORMAT=40, # Set status packet format - parameter follows 
)

TURBO_OFF = 0
TURBO_ON = 1

RUN_MODES = [
    "Startup",
    "Startup Fail",
    "Startup OK",
    "Run",
    "Setup",
    "Shutdown OK",
    "Shutdown Fail",
    ]

PHASE_IDS = [
    "Ramp",
    "Cool",
    "Plat",
    "Hold",
    "End",
    "Purge",
    "Delete Phase",
    "Load Program",
    "Save Program",
    "Soak",
    "Wait",
    ]


def checksum(byte_list, basis=1):
    """
    compute checksum modulo `basis` bytes
    """
    limit = 2**(8*basis)
    return sum([c for c in byte_list]) % limit


def getActiveIPconnections():
    """
    get the list of IP numbers that have established connections

    * exclude any local network interfaces
    * return list sorted by greatest number of established connections
    """
    ip_dict = collections.defaultdict(int)
    for conn in psutil.net_connections():
        ip = conn.laddr.ip
        if (
                conn.family == 2 
                and ip.split(".")[0] not in "0 127 169".split()
                and conn.status == "ESTABLISHED"
            ):
            ip_dict[ip] += 1
    def sorter(ip):
        return ip_dict[ip]
    return sorted(list(ip_dict.keys()), key=sorter, reverse=True)


def getActiveNetworkInterfaces():
    """
    return list of the active network interfaces, excluding local or loopback
    """
    active_ip_connections = getActiveIPconnections()

    interfaces = psutil.net_if_addrs()
    active_interfaces = {}
    for k, nic in interfaces.items():
        for conn in nic:
            if conn.address in active_ip_connections:
                active_interfaces[k] = True
    return list(active_interfaces.keys())


def get_mac():
    """
    return a list of the active MAC addresses, sorted by most connections first

    see also: https://stackoverflow.com/a/41076835/1046449
    """
    excluded_inet_connection_families = [
        socket.AddressFamily.AF_INET,
        socket.AddressFamily.AF_INET6,
        ]
    hexadecimal_characters = "0123456789abcdef"

    interfaces = psutil.net_if_addrs()
    macs = []
    for nic in getActiveNetworkInterfaces():
        for conn in interfaces[nic]:
            # find the MAC address by excluding the other connections
            if conn.family not in excluded_inet_connection_families:
                mac = "".join([
                    c
                    for c in conn.address
                    if c.lower() in hexadecimal_characters])
                if len(mac) == 12:
                    macs.append(mac)

    return macs


def i2bs(i):
    """
    convert integer to byte string

    inverse of bs2i()
    """
    bs = []
    while i > 0:
        bs.append(i % 256)
        i = i // 256
    return bytes(reversed(bs))


def bs2i(bs):
    """
    convert byte string to integer

    inverse of i2bs()
    """
    i = 0
    for b in bs:
        i = i*256 + b
    return i


def getStatusIds():
    "return a dictionary of status ID symbols and ID codes"
    path = os.path.dirname(__file__)
    with open(os.path.join(path, "status_ids.json"), "r") as fp:
        status_ids = json.load(fp)
    for k, v in status_ids.items():
        status_ids[k] = i2bs(v)
    
    return status_ids


def encode2bytes(n):
    """encode `n` as byte string with length 2"""
    if n < 0:
        raise ValueError("value must be positive, received {}".format(n))
    if n > 255:
        return i2bs(n)
    else:
        return bytes((0, n))


STATUS_IDS = getStatusIds()
COMMAND_IDS = {k: encode2bytes(v) for k, v in COMMAND_IDS.items()}


if __name__ == "__main__":
    print(get_mac())
