"""
####################
The Core Fabric File
####################

This Fabric file ('fabfile') goes through your settings file to determine what modules you've included, and allows
one to call the same command on each of these modules.

Calling ``deploy()``, for example, will result in each respective module's own ``deploy()`` method being called.

.. _operating-methods:

=================
Operating Methods
=================
Each module has the following operating methods

* ``bootstrap`` - usually only called once during the life of the server.
  Performs initial installation actions (such as installing packages, uploading templates, configuring of settings)
* ``deploy`` - Called regularly.  This action updates the code/software/data that the module acts on.
  For example: a deploy call in the django module would result in the latest code being checked out from your git
  repository and your settings.py (or localsettings.py) file being updated.
* ``stop`` - Usually used only by service type modules.  For example in the web module, this would *stop*
  the httpd service
* ``start`` - Usually used only by service type modules.  As above, but would *start* the httpd service.


=================
The settings file
=================

A module's operating methods (bootstrap, deploy, start, stop) are special in that they each take care to initialize
the fabric env object correctly for their module.

The settings.py file for Deploy Tools allows the user to customize how the fabric env object is configured.  Each
module has some unique fields that can be specified in the settings file.

For example, in the :ref:`Django Module <django-module-settings>` the following settings can be configured:
::

    DJANGO_GIT_REPO_URL = "git://your/repo.git" #django project repo url
    DJANGO_SUDO_USER = "some_user"
    DJANGO_STAGING_GIT_BRANCH = "develop"
    DJANGO_STAGING_SERVER_NAME = "staging.some_project.com"
    DJANGO_PRODUCTION_GIT_BRANCH = "master"
    DJANGO_PRODUCTION_SERVER_NAME = "production.some_project.com"
    DJANGO_GUNICORN_PORT = '9010'

(Have a look at the settings.py.example file found in the root of this project for an example deployment setup).

In addition to providing values for each module's settings, you also need to specify which modules deploy_tools should use,
by modifying the ``MODULES`` field in settings.py::

    #Deploy modules we'll be utilizing in this project
    MODULES = ["modules.os",
               "modules.web",
               "modules.util",
               "modules.django",
               "modules.packages"]

As with django, it's possible to author your own modules and plug them into this list.


====================
Other Usage Examples
====================

----------------------------
Triggering a specific module
----------------------------
Occasionally you may want to perform an operating method on a single module.  Doing so is straightforward::

    $ fab production deploy:django

This causes the Django module to run it's ``deploy`` operating method for a production-level remote host.
Where ``deploy`` is the operating method that we want to run, and ``django`` is the module we would like to run it on.

--------------------------------
Trigger a module specific action
--------------------------------

Sometimes modules have additional extra methods that don't fit with/fall into the bootstrap/deploy/start/stop paradigm.

Deploy_tools makes it possible to run these specific commands while still utilizing the overall configuration settings in
*settings.py*::

    $ fab production run_command:do_foo,module=django,extra1=bar,extra2=bees

This will cause the *django* module (specified with the ``module=...`` arg to execute ``do_foo``.  Additional arguments,
``extra1`` and ``extra 2`` in this case, are passed on to the special command (``do_foo``) within the module (*django*).

===============
Fabfile Methods
===============

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
    env.show = ['debug']
    _setup_paths()

def production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.server_name = 'project-production.dimagi.com'
    env.hosts = deploy_settings.PRODUCTION_HOST
    env.deploy_level = 'production'
    _setup_env()

def staging():
    env.environment = 'staging'
    env.server_name = 'project-staging.dimagi.com'
    env.hosts = deploy_settings.STAGING_HOST
    env.deploy_level = 'staging'
    _setup_env()

def _setup_paths():
    """
    Creates all the various paths that will be needed
    in deploying code, populating config templates, etc.
    """
    # using posixpath to ensure unix style slashes. See bug-ticket: http://code.fabfile.org/attachments/61/posixpath.patch
    env.project_root = deploy_settings.PROJECT_ROOT
    env.www_root = posixpath.join(env.project_root,'www',env.environment)
    env.log_dir = posixpath.join(env.www_root,'log')
    env.code_root = posixpath.join(env.www_root,'code_root')
    env.project_media = posixpath.join(env.code_root, 'media')
    env.project_static = posixpath.join(env.project_root, 'static')
    env.virtualenv_root = posixpath.join(env.www_root, 'python_env')
    env.services = posixpath.join(env.project_root, 'services')

def run_command(cmd,module=None,*args,**kwargs):
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
            print 'Module is: %s, args: %s, kwargs: %s' % (mod, args, kwargs)
            getattr(mod,cmd)(*args,**kwargs)
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
    run_command('deploy',module,deploy_level=env.deploy_level)


def bootstrap(module=None):
    """
    Runs the bootstrap command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    Bootstrapping is usually associated with initial setup or
    the module being called upon for the first time.
    """
    run_command('bootstrap',module,deploy_level=env.deploy_level)


def start(module=None):
    """
    Runs the start command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    'Starting' is usually associated with services that can be started/stopped. (Useful for restarting services manually)
    """
    run_command('start',module,deploy_level=env.deploy_level)

def stop(module=None):
    """
    Runs the stop command for each module.

    If 'module' argument is specified, this command will only be run for that specific module.

    'Stopping' is usually associated with services that can be started/stopped. (Useful for restarting services manually)
    """
    run_command('stop', module, deploy_level=env.deploy_level)


