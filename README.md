# EventGhostLG
Event Ghost plugin for LG sound bars

To install, copy the lg directory to your EventGhost plugins directory and restart EventGhost. The plugin should only need an ip address to function.

All values are initially read into a cache, and after that, any subsequent events are published as EventGhost events.

This plugin tweaks and includes python-temescal (by Matthew Garrett [mjg59](https://github.com/mjg59)) found [here](https://github.com/mjg59/python-temescal) to work with the older python that Event Ghost uses. Also includes the power function in from [this](https://github.com/mjg59/python-temescal/pull/1) pull request.
