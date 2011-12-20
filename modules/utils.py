"""
Utility functions
(e.g. Determining the remote system OS
"""

from fabric.context_managers import *
from fabric.operations import *



def what_os():
    """
    Returns a string indicating the Host OS.  Currently
    Only supports 'redhat' and 'ubuntu'
    """
    with settings(
        hide('warnings', 'running', 'stdout', 'stderr'),
        warn_only=True
    ):
        if run('ls /etc/lsb-release'):
            return 'ubuntu'
        elif run('ls /etc/redhat-release'):
            return 'redhat'