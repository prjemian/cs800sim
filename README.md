# cs800sim
Simulate the UDP communications and temperature control of a CS800 controller

CONTENTS

- [cs800sim](#cs800sim)
  - [Overview](#overview)
    - [identification](#identification)
    - [status](#status)
    - [control](#control)
  - [Simulation](#simulation)

## Overview

The CS800 controller communicates on the network using UDP.
There are three types of communication, each using a specific port.

port | type | communication
---- | ---- | ----
30303 | broadcast | identification
30304 | broadcast | status
30305 | directed | control

### identification

The controller identifies itself by broadcasting its NetBIOS 
name and MAC address.  This information is repeated by UDP 
broadcast every 1 second to port 30303.

### status

The controller reports its status in UDP broadcasts
every 1 second to port 30304.  The binary format is:

<!--
    Markdown does not support nested tables directly.
    Markdown allows embedded HTML.
    Write the nested table content with HTML.
-->

bits | description
---- | ----
16 | header: `0xAAAB`
16 | data size
repeating | for all parameters:<br /> <table> <thead>  <tr>  <th>bits</th>  <th>description</th>  </tr>  </thead> <tbody> <tr> <td>16</td> <td>parameter ID</td> </tr> <tr> <td>16</td> <td>value</td> </tr> </tbody> </table>
16 | checksum: sum of all parameter IDs and values
16 | footer: `0xABAA`


### control

Control information is communicated with the controller
by UDP over port 30305.  The The binary format is:

bits | description
---- | ----
16 | command ID
16 | argument 1
16 | argument 2
8 | checksum: sum of command ID and arguments


## Simulation

The functions of the temperature controls are simulated, as well as the
command set necessary to simulate temperature control.  Random noise is applied
to the simulated temperature measurement to the level of 0.1 K.
