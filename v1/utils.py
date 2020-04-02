#!/usr/bin/env python

"""
utilities
"""


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
