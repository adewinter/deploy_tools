"""
This module is intended to install and configure RabbitMQ/Celery stuff.  Not finished yet.
"""

from __future__ import absolute_import
import os
import posixpath
from fabric.context_managers import cd, show
from fabric.contrib.files import uncomment
from fabric.operations import sudo, require, put
from fabric.state import env
from fabric.contrib import files
from fabric.colors import green
from modules.utils import what_os
import settings


def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        raise Exception("Unrecognized Deploy Level: %s" % deploy_level)

    env.user = settings.PROJECT_USER
    env.sudo_user = settings.SUDO_USER
    env.os = what_os()
    env.project = settings.PROJECT_NAME
    env.project_root = settings.PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
    env.sudo_user = settings.SUDO_USER
    _setup_path()


def _production():
    """ use production environment on remote host"""
    env.environment = 'production'
    env.server_name = 'project-production.dimagi.com'
    env.hosts = [settings.PRODUCTION_HOST]

def _staging():
    """ use staging environment on remote host"""
    env.environment = 'staging'
    env.server_name = 'project-staging.dimagi.com'
    env.hosts = [settings.STAGING_HOST]

def _setup_path():
    """
    Creates all the various paths that will be needed
    in deploying code, populating config templates, etc.
    """
    # using posixpath to ensure unix style slashes. See bug-ticket: http://code.fabfile.org/attachments/61/posixpath.patch
    env.project_root = settings.PROJECT_ROOT
    env.www_root = posixpath.join(env.project_root,'www',env.environment)
    env.log_dir = posixpath.join(env.www_root,'log')
    env.code_root = posixpath.join(env.www_root,'code_root')
    env.local_settings_folder = os.path.split(os.path.abspath(settings.__file__))[0]
    env.virtualenv_name = getattr(settings, 'PYTHON_ENV_NAME', 'python_env') #not a required setting and should be sufficient with default name
    env.virtualenv_root = posixpath.join(env.www_root, env.virtualenv_name)
    env.services_root = posixpath.join(env.project_root, 'services')


def bootstrap(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    print green("In Example Module, bootstrap().  Doing Nothing.")


def develop(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    print green("In Example Module, develop().  Doing Nothing.")


def stop(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    print green("In Example Module, stop().  Doing Nothing.")


def start(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    print green("In Example Module, start().  Doing Nothing.")