# cs800sim
simulate the CS800 controller UDP communications

The CS800 controller communicates on the network using UDP.
There are three types of communication, each using a specific port.

port | type | communication
---- | ---- | ----
30303 | broadcast | identification
30304 | broadcast | status
30305 | directed | control

## identification

The controller identifies itself by broadcasting its NetBIOS 
name and MAC address.  This information is repeated by UDP 
broadcast every 1 second to port 30303.

## status

The controller reports its status in UDP broadcasts
every 1 second to port 30304.  The format is ...

## control

Control information is communicated with the controller
by UDP over port 30305.  The format is ...
