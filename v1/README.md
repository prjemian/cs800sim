# CS800 Simulator

These files provide simulators for the CS800 controller
to support identity broadcasts, status broadcasts, and
commands.

## Controller

A controller broadcasts identity and status every second
and can receive commands.  No response to commands is given,
other than how the controller status is changed.

To manage all these activities in one python program,
each should be run in a separate thread.

activity | code
---- | ----
identity | `emit_id.announcer()`
status | `broadcast_status.CS800().emit_status()`
commands | `controller.CS800controller().handler()`
all 3 | `cs800.main()`

## Client

A client can listen for broadcasts of identity and status and
can send commands to specific controllers addressed by IP number.
