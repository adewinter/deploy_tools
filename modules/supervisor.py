"""
Oh, god. Supervisord.
"""
import posixpath
from fabric.operations import sudo
from fabric.state import env
from fabric.contrib import files
from fabric.colors import green

def init():
    pass

def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    if not files.exists(env.log_dir):
        print green('Log Directory (%s) does not exist on host, creating...' % env.log_dir)
        sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
        sudo('chmod a+w %(log_dir)s' % env, user=env.sudo_user)

    if not files.exists(env.services_supervisor):
        print green('Supervisor services (%s) folder does not exist. Creating...' % env.services_supervisor)
        sudo('mkdir -p %(services)s/supervisor' % env, user=env.sudo_user)