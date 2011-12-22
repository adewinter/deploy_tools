"""
Deals with pip requirements.
(Initial installing, refreshing, etc)

Packages Module Settings
----------------------------------------------
::

    PACKAGES_PIP_REQUIREMENTS_PATH = "pip_requires.txt" #The path to pip_requires file ON THE LOCAL Machine, relative to this settings.py file.
"""
from fabric.api import *
from fabric.colors import green
from fabric import utils
from fabric.main import files
import posixpath
from modules.utils import what_os
import os

def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        utils.abort("Unrecognized Deploy Level: %s" % deploy_level)
    env.project = settings.DJANGO_PROJECT_NAME
    env.pip_requirements_local_path = settings.PACKAGES_PIP_REQUIREMENTS_PATH  #this is the local machine requires file path
    env.project_user = settings.PROJECT_USER
    env.sudo_user = settings.SUDO_USER
    env.os = what_os()
    env.project_root = settings.PACKAGES_PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
    env.virtuanlenv_name = getattr(settings, 'PYTHON_ENV_NAME', 'python_env')
    env.virtualenv_root = posixpath.join(env.project_root, env.virtualenv_name)

def _production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.server_name = 'project-production.dimagi.com'
    env.hosts = settings.PRODUCTION_HOST


def _staging():
    """ use staging environment on remote host"""
    env.environment = 'staging'
    env.server_name = 'project-staging.dimagi.com'
    env.hosts = settings.STAGING_HOST

def upload_pip_requires():
    """
    Uploads the pip requirements file to the host machine and sets
    the relevant env variables
    """
    require('pip_requirements_local_path', provided_by='setup_env')
    pip_filename, tail = os.path.split(env.pip_requirements_local_path)
    with cd('/tmp'):
        put(env.pip_requirements_local_path,'')
    env.pip_requirements_remote_path = posixpath.join('/tmp', pip_filename)

def install_packages():
    """Install packages, given a list of package names"""
    upload_pip_requires()
    with cd(env.project_root):
        sudo('pip install -E %(virtualenv_root)s --requirement %(pip_requirements_remote_path)s' % env, user=env.sudo_user, pty=True, shell=True)

def create_directories():
    require('environment', provided_by=('setup_env'))
    require('root',provided_by=('setup_env'))
    sudo('mkdir -p %(project_root)s' % env, user=env.sudo_user)


def setup_virtualenv():
    """
    Initially creates the virtualenv in the correct places (creating directory structures as necessary) on the
    remote host
    """
    print green('In packages module.  Installing VirtualEnv on host machine...')
    require('virtualenv_root', provided_by=('setup_env'))
    args = '--clear --distribute --no-site-packages'
    sudo('virtualenv %s %s' % (args, env.virtualenv_root), user=env.sudo_user)
    print green('In packages module. Done installing VirtualEnv...')

def bootstrap(deploy_level='staging'):
    """
    Performs initial install of virtualenv, then installs listed pip packages specified in settings file
    """
    print green('In Packages Module. Running bootstrap()...')
    setup_env(deploy_level)
    create_directories()
    setup_virtualenv()
    install_packages()
    print green('In Packages Module. Done running bootstrap()...')

def deploy(deploy_level='staging'):
    """
    Installs all packages listed in the pip packages list file(s) specified in settings.
    """
    print green('In Packages Module. Running deploy()...')
    setup_env(deploy_level)
    install_packages()
    print green('In Packages Module. Done running deploy()...')

def stop():
    """
    Does nothing in this module
    """
    print green('In Packages Module. Doing nothing for command stop()')


def start():
    """
    Does nothing in this module
    """
    print green('In Packages Module. Doing nothing for command start()')