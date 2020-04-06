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
import time

import broadcast_status
import controller
import emit_id


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

cs800_status = None
cs800_commands = None


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
    global cs800_status
    cs800_status = broadcast_status.CS800()
    cs800_status.emit_status()


def receiver(results):
    logger.info(results)
    cmd = results.get("command_id")
    if cmd == "COOL":
        sp = results["arg1"] * 0.01
        cs800_status.memory["StatusGasSetPoint"] = sp
    elif cmd == "RAMP":
        sp = results["arg2"] * 0.01
        # TODO: simulate arg1, K/hour ramp rate
        cs800_status.memory["StatusGasSetPoint"] = sp


def commands():
    global cs800_commands
    cs800_commands = controller.CS800controller()
    cs800_commands.handler(receiver)


def main():
    global cs800_status
    identity()
    status()
    while cs800_status is None:
        logger.info("waiting for threads to start ...")
        time.sleep(1)   # let threads start
    logger.info("Emitting ID & status, waiting for commands...")
    cs800_status.run_mode = "Startup OK"
    commands()


if __name__ == "__main__":
    main()
