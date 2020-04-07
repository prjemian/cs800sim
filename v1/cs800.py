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


class StateMachine:
    """
    State machine to process commands

    ==============  ========================
    Command Name    Meaning
    ==============  ========================
    RESTART         Stop Cryostream and re-initialise system back to “Ready”. 
    RAMP            Change gas temperature to a set value at a controlled rate. 
    COOL            Make gas temperature decrease to a set value as quickly as possible. 
    PLAT            Maintain the current temperature for a set amount of time. 
    PAUSE           Interrupt the current commands and maintain the current gas temperature until instructed otherwise by a RESUME command. 
    RESUME          Resume the previous command before the PAUSE command was given. 
    HOLD            Stay at the current temperature indefinitely with no ability to resume the previous command (unlike the PAUSE and RESUME functions). 
    END             Bring the gas temperature to 300 K, then shut down. 
    PURGE           Bring the gas temperature and the internal temperature to 300 K then shut down. 
    ==============  ========================
    """

    def __init__(self):
        self.queue = []
        self.handler = self.idle
        self.loop_delay = 0.1
        self.command_process_delay = 1.0

        self.phase_id_paused = None
        self.setpoint_target_time = 0.0
        self.ramp_rate = 0
        self.ramp_setpoint = 0

        # TODO:
        self.pause = False

        self.event_loop()

    def addCommand(self, request):
        "add a command request to the queue"
        cmd = request.get("command_id")
        if cmd == "PAUSE":
            self.do_pause()
        elif cmd == "RESUME":
            self.do_resume()
        else:
            self.queue.append(request)

    @run_in_thread
    def event_loop(self):
        logger.info("event loop started ...")
        timer = time.time() + self.command_process_delay
        while True:
            if time.time() > timer:
                timer += self.command_process_delay
                self.handler()
            time.sleep(self.loop_delay)
    
    def idle(self):
        if len(self.queue) == 0:
            return                      # nothing to do

        request = self.queue.pop(0)     # next request in the queue
        logger.info(request)

        cmd = request.get("command_id")
        if cmd == "COOL":
            rate = 360.0                    # K/h
            sp = request["arg1"] * 0.01     # K
            cs800_status.phase_id = "Cool"
            cs800_status.memory["StatusGasSetPoint"] = sp

        elif cmd == "RAMP":
            self.ramp_rate = request["arg1"]          # K/h
            self.ramp_setpoint = request["arg2"] * 0.01     # K
            sp_now = cs800_status.memory["StatusGasSetPoint"]

            # FIXME:
            # self.time_remaining = (sp - sp_now) / rate / 3600.0
            # self.setpoint_target_time = time.time() + self.time_remaining

            cs800_status.memory["StatusGasSetPoint"] = self.ramp_setpoint
            cs800_status.memory["StatusRampRate"] = self.ramp_rate

            cs800_status.phase_id = "Ramp"
            # self.handler = self.do_ramp

        elif cmd == "END":
            cs800_status.phase_id = "End"
            # TODO:

        elif cmd == "HOLD":
            cs800_status.phase_id = "Hold"
            # TODO:

        elif cmd == "PLAT":
            cs800_status.phase_id = "Plat"
            # TODO:

        elif cmd == "PURGE":
            cs800_status.phase_id = "Purge"
            # TODO:
    
    def do_cool(self):
        pass
    
    def do_ramp(self):
        time_left = self.setpoint_target_time - time.time()
        if time_left < 0:
            self.handler = self.idle
            self.setpoint_target_time = 0
            return
        # sp = cs800_status.memory["StatusGasSetPoint"]
        # cs800_status.memory["StatusGasSetPoint"] = sp

    def do_pause(self):
        # TODO:
        self.phase_id_paused = cs800_status.phase_id
        # remember to keep track of where we were for RESUME
        cs800_status.phase_id = "Wait"
    
    def do_resume(self):
        # TODO:
        cs800_status.phase_id = self.phase_id_paused
        self.phase_id_paused = None


@run_in_thread
def identity():
    emit_id.announcer()


@run_in_thread
def status():
    global cs800_status
    cs800_status = broadcast_status.CS800()
    cs800_status.emit_status()


def commands():
    global cs800_commands
    state_machine = StateMachine()
    cs800_commands = controller.CS800controller()
    cs800_commands.handler(state_machine.addCommand)


def main():
    global cs800_status
    identity()
    status()
    while cs800_status is None:
        logger.info("waiting for threads to start ...")
        time.sleep(1)   # let threads start
    logger.info("Emitting ID & status, waiting for commands...")
    cs800_status.run_mode = "Startup OK"
    time.sleep(1)
    cs800_status.run_mode = "Run"
    commands()


if __name__ == "__main__":
    main()
