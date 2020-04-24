#!/usr/bin/env python

"""
ophyd script to watch CS800 simulators
"""

import logging
import ophyd
import time

# logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_l = logging.getLogger("ophyd")
_l.setLevel(logging.WARN)


class CS800(ophyd.Device):
    buffer = ophyd.Component(ophyd.EpicsSignal, ".BINP", kind="config")
    ieos = ophyd.Component(ophyd.EpicsSignal, ".IEOS", kind="config")
    ifmt = ophyd.Component(ophyd.EpicsSignal, ".IFMT", kind="config")
    nrrd = ophyd.Component(ophyd.EpicsSignal, ".NRRD", kind="config")
    proc = ophyd.Component(ophyd.EpicsSignal, ".PROC", kind="config")
    scan = ophyd.Component(ophyd.EpicsSignal, ".SCAN", kind="config")
    tmod = ophyd.Component(ophyd.EpicsSignal, ".TMOD", kind="config")

    alarm_code = ophyd.Component(ophyd.Signal, value=0)
    cid = ophyd.Component(ophyd.Signal, value=0)
    # mac = ophyd.Component(ophyd.Signal, value="unknown")
    phase = ophyd.Component(ophyd.Signal, value="")
    setpoint = ophyd.Component(ophyd.Signal, value=0)
    temperature = ophyd.Component(ophyd.Signal, value=0)

    cksum = -1
    params = {}

    _phase_ids = [
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


    def listen(self, value=[], timestamp=None, **kwargs):
        buf = self.buffer.get()
        if len(buf) != 928:
            logger.debug("not exactly 928 bytes: %d", len(buf))
            return

        def uint16(i):
            "convert two bytes at offset i to a 16-bit unsigned integer"
            return buf[i]*256+buf[i+1]

        def bykey(pid, default=None):
            "return parameter by parameter ID"
            try:
                par = param[pid]
                return par
            except KeyError:
                logger.debug("paramID %d not found: number of parameters = %d", pid, len(param))

        param = {}
        for i in range(4, 924, 4):
            param[uint16(i)] = uint16(i+2)
        if len(param) != 230:
            logger.debug("expected 230 parameters, found %d", len(param))
            return

        cid = param.get(1028)
        if self.cid.get() > 0 and cid != self.cid.get():
            # filter out packets from other controllers
            return
        logger.debug("checkpoint %d", cid)

        csum = uint16(924)
        # if csum == self.cksum:
        #     logger.debug("checksum not changed")
        #     return

        self.cksum = csum
        self.params = param

        phase_code = bykey(1054, -1)
        if phase_code is not None and phase_code in range(0, len(self._phase_ids)):
            phase = self._phase_ids[phase_code]
        else:
            phase = f"phase:{phase_code}"

        self.alarm_code.put(bykey(1065))
        # self.mac.put(f"{param[1311]:04x}{param[1312]:04x}{param[1313]:04x}")
        self.phase.put(phase)
        self.setpoint.put(param[1050]*0.01)
        self.temperature.put(param[1051]*0.01)

        logger.info("update: %s", str(self.succinct()))

    def setup(self, cid):
        self.cid.put(cid)
        self.wait_for_connection()
        self.nrrd.put(928)
        self.ifmt.put("Binary")
        # self.scan.put("I/O Intr")
        self.tmod.put("Read")
        self.proc.put(1)
        self.buffer.subscribe(self.listen)

    def succinct(self):
        # return self.read()
        dt = self.temperature.timestamp - t0
        return (
            "("
            f"{dt:03f}"
            f",{self.cid.get()}"
            f",{self.params.get(1028,0)}"
            # f"{self.mac.get()}"
            f",{hex(self.cksum)}"
            "):"
            f" {self.alarm_code.get()}"
            f" {self.phase.get()}"
            f" {self.setpoint.get():.02f}"
            f" {self.temperature.get():.02f}"
            )


ONE_SECOND = 1
ONE_MINUTE = 60 * ONE_SECOND
TEN_MINUTES = 10 * ONE_MINUTE

if __name__ == "__main__":
    t0 = time.time()
    t_quit = t0 + 10*ONE_SECOND
    # t_quit = t0 + TEN_MINUTES

    # cs144 = CS800("cs800:CS:ASYN:SP", name="cs144")
    # cs144.setup(144)
    # cs113 = CS800("cs113:CS:ASYN:SP", name="cs113")
    # cs113.setup(113)

    xxx_asyn = CS800("xxx:asyn", name="xxx_asyn")

    while time.time() < t_quit:
        time.sleep(0.1)
