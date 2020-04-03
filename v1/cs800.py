#!/usr/bin/env python

"""
support all UDP interfaces of a CS800 controller

activity | code
---- | ----
identity | `emit_id.announcer()`
status | `broadcast_status.CS800().emit_status()`
commands | `controller.CS800controller().handler()`
"""

import logging
import threading

import broadcast_status
import controller
import emit_id


# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)
# logger.setLevel(logging.DEBUG)


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    
    USAGE::
       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       
       #...
       progress_reporting()   # runs in separate thread
       #...

       see: https://github.com/BCDA-APS/apstools/blob/master/apstools/utils.py
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


@run_in_thread
def identity():
    emit_id.announcer()


@run_in_thread
def status():
    cs800 = broadcast_status.CS800()
    cs800.emit_status()


def receiver(results):
    print(results)


def commands():
    cs800 = controller.CS800controller()
    cs800.handler(receiver)


def main():
    identity()
    status()
    commands()


if __name__ == "__main__":
    main()
