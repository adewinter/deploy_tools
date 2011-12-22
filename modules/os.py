"""
OS Level Operations.
Creates required users
Installs base packages
Misc OS level config

OS MODULE SPECIFIC SETTINGS
---------------------------
::

   OS_PACKAGE_LIST_PATH_REDHAT = "yum_packages.txt" #each package on a new line in this file
   OS_PACKAGE_LIST_PATH_UBUNTU = "apt_packages.txt" #each package on a new line in this file

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

def install_packages():
    """Install packages, given a list of package names"""
    require('package_install_command', provided_by=('setup_env'))
    with open(env.packages_list) as f:
        packages = f.readlines()
    env.packages_to_install = " ".join(map(lambda x: x.strip('\n\r'), packages))
    sudo('%(package_install_command)s %(packages_to_install)s' % env)

def bootstrap(deploy_level='staging'):
    """
    Installs all packages listed in the OS packages list file(s) specified in settings.
    """
    print green('In OS Module. Running bootstrap()...')
    setup_env(deploy_level)
    install_packages()

def deploy(deploy_level='staging'):
    """
    Does the same thing as bootstrap.  Installs all packages listed in the OS packages list file(s) specified in settings.
    """
    print green('In OS Module. Running deploy()...')
    setup_env(deploy_level)
    install_packages()

def stop():
    """
        Does nothing in this module
    """
    print green('In OS Module. Doing nothing for command stop()')


def start():
    """
        Does nothing in this module
    """
    print green('In OS Module. Doing nothing for command start()')