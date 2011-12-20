"""
Django deployment module.
Creates necessary folders for housing project source code
clones, deploys, submodule checkouts
"""

from fabric.api import *
from fabric.colors import green
from fabric.contrib import files, console
from fabric.contrib.project import rsync_project
from fabric import utils
from fabric.decorators import hosts
import posixpath

def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        raise Exception("Unrecognized Deploy Level: %s" % deploy_level)

    env.sudo_user = settings.DJANGO_SUDO_USER
    env.code_repo = settings.DJANGO_GIT_REPO
    env.project = settings.DJANGO_PROJECT_NAME
    env.server_port = settings.DJANGO_GUNICORN_PORT
    env.settings = '%(project)s.localsettings' % env
    env.db = '%s_%s' % (env.project, env.environment)

    _setup_path()


def _setup_path():
    """
    Creates all the various paths that will be needed
    in deploying code, populating config templates, etc.
    """
    env.module_folder = posixpath.dirname(__file__)
    env.deploy_root = posixpath.split(env.module_folder)
    env.home = posixpath.split(settings.DJANGO_PROJECT_HOME)
    # using posixpath to ensure unix style slashes. See bug-ticket: http://code.fabfile.org/attachments/61/posixpath.patch
    env.root = posixpath.join(env.home, 'www', env.environment)
    env.log_dir = posixpath.join(env.home, 'www', env.environment, 'log')
    env.code_root = posixpath.join(env.root, 'code_root')
    env.project_root = posixpath.join(env.code_root, env.project)
    env.project_media = posixpath.join(env.code_root, 'media')
    env.project_static = posixpath.join(env.project_root, 'static')
    env.virtualenv_root = posixpath.join(env.root, 'python_env')
    env.services = posixpath.join(env.home, 'services')

def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    require('root',provided_by=('setup_env'))
    if not files.exists(env.root):
        sudo('mkdir -p %(root)s' % env, user=env.sudo_user)
    if not files.exists(env.log_dir):
        sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
    sudo('chmod a+w %(log_dir)s' % env, user=env.sudo_user)


def _production():
    """ use production environment on remote host"""
    env.code_branch = settings.DJANGO_PRODUCTION_GIT_BRANCH
    env.environment = 'production'
    env.server_name = 'project-production.dimagi.com'
    env.hosts = [settings.PRODUCTION_HOST]

def _staging():
    """ use staging environment on remote host"""
    env.code_branch = settings.DJANGO_STAGING_GIT_BRANCH
    env.environment = 'staging'
    env.server_name = 'project-staging.dimagi.com'
    env.hosts = [settings.STAGING_HOST]

def collectstatic():
    """ run collectstatic on remote environment. ASSUMES YOU ALREADY HAVE ALL REQUIRED PACKAGES AND VIRTUALENV INSTALLED. """
    require('project_root', provided_by=('setup_env'))
    with cd(env.project_root):
        sudo('%(virtualenv_root)s/bin/python manage.py collectstatic --noinput --settings=%(settings)s' % env, user=env.sudo_user)

def clone_repo():
    """ clone a new copy of the git repository """
    require('root', provided_by=('setup_env'))
    with cd(env.root):
        sudo('git clone %(code_repo)s %(code_root)s' % env, user=env.sudo_user)

def deploy(deploy_level="staging"):
    """ deploy code to remote host by checking out the latest via git """
    setup_env(deploy_level)
    print green('In Django Module. Running deploy()...')
    sudo('echo ping!') #hack/workaround for delayed console response
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy production?',
                               default=False):
            utils.abort('Production deployment aborted.')

    with cd(env.code_root):
        sudo('git checkout %(code_branch)s' % env, user=env.sudo_user)
        sudo('git pull', user=env.sudo_user)
        sudo('git submodule init', user=env.sudo_user)
        sudo('git submodule update', user=env.sudo_user)
            
    collectstatic()

def bootstrap(deploy_level="staging"):
    """
    Creates initial folders, clones the git repo. DOES NOT DEPLOY()
    """
    setup_env(deploy_level)
    print green('In Django Module. Running bootstrap()...')
    sudo('echo ping!') #hack/workaround for delayed console response
    if env.environment == 'production':
        if not console.confirm('Are you sure you want to deploy production?',
                               default=False):
            utils.abort('Production deployment aborted.')

    setup_dirs()
    clone_repo()


def stop():
    """
        Does nothing in this module
    """
    print green('In Django Module. Doing nothing for command stop().')


def start():
    """
        Does nothing in this module
    """
    print green('In Django Module. Doing nothing for command start().')