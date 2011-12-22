Dimagi Deploy Tools
===================

This is a toolset based on Fabric that allows us to rapidly deploy our various Django projects.

This tool is essentially a set of modules that are easily configurable in a central place (the settings.py file).
Modules can rely on templates to upload configuration specific files (e.g. a supervisord.conf file), and these templates can
be version controlled in a wholly seperate folder on disk.

Full usage documentation can be found [here](http://dimagi-deployment-tools.readthedocs.org/).