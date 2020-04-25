
# Example IOC shell commands

These are from the Stream support

```
# ### cs800.iocsh ###
# STATUS_ADDR  "255.255.255.255:30304:30304 UDP"
# COMMAND_ADDR "10.0.0.173:30305 UDP*"
# Status Packets
drvAsynIPPortConfigure("OC_SP", "192.168.144.144:30304:30304 UDP&", 0, 0, 0)
# Commands
drvAsynIPPortConfigure("OC_CMD", "192.168.144.144:30305 UDP", 0, 0, 0)
#asynSetTraceIOMask("OC_SP", 0, 2)
#asynSetTraceMask("OC_SP", 0, 9)
#asynSetTraceIOMask("OC_CMD", 0, 2)
#asynSetTraceMask("OC_CMD", 0, 9)
dbLoadRecords("/usr/local/epics/synApps_6_1/support/asyn-git/db/asynRecord.db","P=cs800:,R=CS:ASYN:SP,PORT=OC_SP,ADDR=0,OMAX=1000,IMAX=1000")
dbLoadRecords("/usr/local/epics/synApps_6_1/support/asyn-git/db/asynRecord.db","P=cs800:,R=CS:ASYN:CMD,PORT=OC_CMD,ADDR=0,OMAX=1000,IMAX=1000")
epicsEnvSet("STREAM_PROTOCOL_PATH", ".:/usr/local/epics/synApps_6_1/support/ip-git/ipApp/Db")
dbLoadRecords("/usr/local/epics/synApps_6_1/support/ip-git/db/Oxford_CS800.db", "P=cs800:,Q=CS,PORT=OC_SP,PORTCMD=OC_CMD")
```


# Status Packets

Each CS800 controller will broadcast a status packet to the LAN
every one second by UDP on port 30304.  The status packet
has a fixed length and defined format.

## asyn communications

Only one instance of this database per network interface.

file:  `Oxford_CS800_status.db`

```
# P=cs800:                  # IOC prefix
# R=CS:                     # status packets
# PORT=CS800_STATUS_IP      # asyn port name
#
record(asyn,"$(P)$(R)status_packet")
{
    field(DTYP, "asynRecordDevice")
    field(PORT, "$(PORT)")
    field(ADDR, 0)
    field(OMAX, 1000)
    field(IMAX, 1000)
    field(NRRD, 928)
    field(TMOD, "Read")
    field(TMOT, 1.0)
    field(IFMT, "Binary")
    field(SCAN, ".1 second")
    field(PINI, "YES")
}
```

These IOC shell commands connect the status broadcasts 
on UDP port 30304 with a named asyn port and make the 
status packet data available from the BINP field of an 
asyn record.  This becomes a PV (`$(P)$(R)status_packet`) 
for further processing by any/all controllers on the LAN.

```
epicsEnvSet("CS800_IP_STATUS", "192.168.144.255")
drvAsynIPPortConfigure("CS800_STATUS", "$(CS800_IP_STATUS):30304:30304 UDP")
dbLoadRecords("Oxford_CS800_status.db", "P=$(PREFIX),R=CS:,PORT=CS800_STATUS")
epicsEnvSet("CS800_STATUS", "$(PREFIX)CS:")     # for use with each controller
```

# each controller

Each controller will need an EPICS database that provides PVs
for the controller status and commands.  (The existing stream 
protocol) works well for the command processing.  The existing 
stram protocol for status broadcasts does not filter out updates
from other controllers on the LAN.  It will be replaced by SNL
support.)

Each controller support will need it's own asyn IP port 
connection to the controller's UDP port 30305.  Thus, ALL must be
opened with the `UDP&` configuration.

```
epicsEnvSet("CS800_C0_IP", "192.168.144.144")   # IP number
drvAsynIPPortConfigure("CS800_CMD0", "$(CS800_C0_IP):30305 UDP&")
dbLoadRecords("Oxford_CS800_controller.db", "P=$(PREFIX),R=CS0:,PORT=CS800_CMD0",SP=$(CS800_STATUS))
epicsEnvSet("CS800_ID_C0", "144")               # Controller ID
# TODO: seq program startup

epicsEnvSet("CS800_C1_IP", "192.168.144.113")   # IP number
drvAsynIPPortConfigure("CS800_CMD1", "$(CS800_C1_IP):30305 UDP&")
dbLoadRecords("Oxford_CS800_controller.db", "P=$(PREFIX),R=CS1:,PORT=CS800_CMD1",SP=$(CS800_STATUS))
epicsEnvSet("CS800_C1_ID", "113")               # Controller ID
# TODO: seq program startup

epicsEnvSet("CS800_C2_IP", "192.168.144.102")   # IP number
drvAsynIPPortConfigure("CS800_CMD2", "$(CS800_C2_IP):30305 UDP&")
dbLoadRecords("Oxford_CS800_controller.db", "P=$(PREFIX),R=CS2:,PORT=CS800_CMD2",SP=$(CS800_STATUS))
epicsEnvSet("CS800_C2_ID", "102")               # Controller ID
# TODO: seq program startup
```

A SNL program will monitor `$(P)$(R)asyn.BINP` and process
the packets from the designated controller ID.
If controller ID of zero is passed, the SNL program will
choose the first controller ID from the first valid packet 
it receives (allows for the default case when only one 
controller exists).

Run a SNL program instance for each controller to be supported.
