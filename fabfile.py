"""
The meat.

Goes through your settings file to determine what modules you've included

If you call 'deploy' here, deploy will variously be called in each module you've listed in settings (if applicable).

E.g. deploy in 'web' will mean a refresh of the HTTPD config file and a restart of the service,
     in 'packages' it will simply mean checking the requirements files specified in settings to make sure everything is up to date.
     in 'django' it will mean checking out the git repo, relevant submodules and a refresh of the localsettings.py file.

Similar concepts apply to 'bootstrap', 'stop', 'start' and 'restart'.
"""

from fabric.api import *
from fabric.colors import red
from fabric.contrib import files, console
from fabric import utils
from fabric.decorators import hosts

from modules.utils import what_os, try_import
import settings as deploy_settings
import posixpath



def _setup_env():
    #set up env based on settings info
    env.deploy_root = posixpath.dirname(__file__)
    env.home = posixpath.split(env.deploy_root)
    env.deploy_modules = deploy_settings.MODULES


def hello():
    print "testing OS:"
    print what_os()
    

def production():
    env.deploy_level = 'production'
    _setup_env()

def staging():
    env.deploy_level = 'staging'
    _setup_env()

def _run_command(cmd,module=None,*args,**kwargs):
    """
    Calls the given command on a single specified module (specified with the 'mod' argument.
    """
    if module is None:
        modules = env.deploy_modules
    else:
        modules = [module]
    for m in modules:
        mod = try_import(m)
        if mod is not None:
            getattr(mod,cmd)(args,kwargs)
        else:
            print red('Failed to import Module: %s. Command "%s" not executed.' % (m, cmd))
            utils.abort('Failed to import Module: %s. Command "%s" not executed.' % (m, cmd))

def deploy(module=None):
    """
    Runs the deploy command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    'Deployment' is usually associated with a refreshing/updating
    of content/data
    """
    _run_command('deploy',module,deploy_level=env.deploy_level)


def bootstrap(module=None):
    """
    Runs the bootstrap command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    Bootstrapping is usually associated with initial setup or
    the module being called upon for the first time.
    """
    _run_command('bootstrap',module,deploy_level=env.deploy_level)


def start(module=None):
    """
    Runs the start command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    'Starting' is usually associated with services that can be started/stopped. (Useful for restarting services manually)
    """
    _run_command('start',module,deploy_level=env.deploy_level)

def stop(module=None):
    """
    Runs the stop command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    'Stopping' is usually associated with services that can be started/stopped. (Useful for restarting services manually)
    """
    _run_command('stop', module, deploy_level=env.deploy_level)


