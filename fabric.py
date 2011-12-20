"""
The meat.

Goes through your settings file to determine what modules you've included

If you call 'deploy' here, deploy will variously be called in each module you've listed in settings (if applicable).

E.g. deploy in 'web' will mean a refresh of the HTTPD config file and a restart of the service,
     in 'packages' it will simply mean checking the requirements files specified in settings to make sure everything is up to date.
     in 'django' it will mean checking out the git repo, relevant submodules and a refresh of the localsettings.py file.

Similar concepts apply to 'bootstrap', 'stop', 'start' and 'restart'.
"""

from deploy.modules.utils import what_os
from settings import *

def init():
    #set up env based on settings info

def hello():
    print "testing OS:"
    print what_os()
    
  