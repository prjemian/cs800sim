#!/usr/bin/env python

"""
utilities
"""

import collections
import psutil
import socket


# def isNicKnownAsInternal(nic_name):
#     """
#     is this network interface name known to be internal?
#     """
#     if nic_name == "lo":
#         return True
#     elif nic_name.startswith("Loopback"):
#         return True
#     elif nic_name.startswith("br-"):
#         return True
#     elif nic_name.startswith("Virtual"):
#         return True
#     elif nic_name.startswith("Bluetooth"):
#         return True
#     elif nic_name.startswith("docker"):
#         return True
#     return False


# def isAddrKnownInternal(nic_addr):
#     """
#     is this network interface known to be internal?
#     """
#     if nic_addr.family not in (2, 17):  # (AF_INET, AF_LINK)
#         return True
#     return False


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


if __name__ == "__main__":
    print(get_mac())
