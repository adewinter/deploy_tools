"""
Deals with pip requirements.
(Initial installing, refreshing, etc)

Packages Module Settings
----------------------------------------------
::

    PACKAGES_PIP_REQUIREMENTS_PATH = "pip_requires.txt" #The path to pip_requires file ON THE LOCAL Machine, relative to this settings.py file.
"""

#Importing the standard OS package conflicts with the 'os' module in the modules folder.
#The solution is found here:
#http://docs.python.org/whatsnew/2.5.html#pep-328-absolute-and-relative-imports
from __future__ import absolute_import
from fabric.api import *
from fabric.colors import green, yellow
from fabric import utils
from fabric.main import files
import posixpath
from modules.utils import what_os


import os
import settings
from fabric.api import settings as fab_settings

def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        utils.abort("Unrecognized Deploy Level: %s" % deploy_level)
    env.pip_requirements_local_path = settings.PACKAGES_PIP_REQUIREMENTS_PATH  #this is the local machine requires file path
    env.project_user = settings.PROJECT_USER
    env.sudo_user = settings.SUDO_USER
    env.os = what_os()

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
    require('pip_requirements_local_path', provided_by=('setup_env'))
    (head, pip_filename) = os.path.split(env.pip_requirements_local_path)
    print 'PIP FILENAME: %s' % pip_filename
    with show('debug'):
        with cd('/tmp'):
            put(env.pip_requirements_local_path,'/tmp/')
    env.pip_requirements_remote_path = posixpath.join('/tmp', pip_filename)

def install_packages():
    """Install packages, given a list of package names"""
    upload_pip_requires()
    with cd(env.project_root):
        with fab_settings(user=env.sudo_user):
            sudo('pip install -E %(virtualenv_root)s --requirement %(pip_requirements_remote_path)s' % env, user=env.sudo_user, pty=True, shell=True)

def create_directories():
    require('environment', provided_by=('setup_env'))
    require('project_root',provided_by=('setup_env'))
    sudo('mkdir -p %(project_root)s' % env, user=env.sudo_user)


def setup_virtualenv():
    """
    Initially creates the virtualenv in the correct places (creating directory structures as necessary) on the
    remote host.
    If necessary, installs setup_tools, then pip, then virtualenv (packages)
    """
    print green('In packages module.  Installing VirtualEnv on host machine...')
    require('virtualenv_root', provided_by=('setup_env'))

    with cd('/tmp'):
        if env.os == 'ubuntu':
            sudo('apt-get install -y python-setuptools python-setuptools-devel')
        elif env.os == 'redhat':
            sudo('yum install -y python-setuptools python-setuptools-devel')
        else:
            utils.abort('Unrecognized OS %s!' % env.os)
        sudo('easy_install pip')
        sudo('pip install virtualenv', pty=True, shell=True)

        print yellow('Require user:%(sudo_user)s password!' % env)
        with fab_settings(user=env.sudo_user, sudo_prompt='ARemind sudo password: ', warn_only=True):
            sudo('mkdir -p %(www_root)s' % env)
            sudo('chown -R %(www_root)s %(virtualenv_root)s' % env)
            sudo('chgrp -R %(www_root)s %(virtualenv_root)s' % env)
            args = '--clear --distribute'
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