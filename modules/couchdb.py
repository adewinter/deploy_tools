"""
CouchDB installation and start/stop ops.
Installs core packages required (like EPEL for RHEL, openssl, etc)
Builds curl
Install couchdb from source (defaults to version 1.1.1)
Create couch user and update permissions
Run + Test
"""
from fabric.api import *
from fabric.colors import green
from fabric import utils
from modules.utils import what_os

def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        utils.abort("Unrecognized Deploy Level: %s" % deploy_level)
    env.os = what_os()
    if env.os == 'ubuntu':
        env.package_list = settings.OS_PACKAGE_LIST_PATH_UBUNTU
        env.package_install_cmd = 'apt_get install -y'
    elif env.os == 'redhat':
        env.package_install_cmd = 'yum install'
        env.package_list = settings.OS_PACKAGE_LIST_PATH_REDHAT
    else:
        utils.abort('Unrecognized OS: %s. Aborting.' % env.os)
    env.project = settings.DJANGO_PROJECT_NAME

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