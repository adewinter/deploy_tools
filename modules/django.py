"""
Django deployment module.
Creates necessary folders for housing project source code
clones, deploys, submodule checkouts

.. _django-module-settings:

Django Module Settings
----------------------
::

    DJANGO_GIT_REPO_URL = "git://your/repo.git" #django project repo url
    DJANGO_STAGING_GIT_BRANCH = "develop"
    DJANGO_STAGING_SERVER_NAME = "staging.some_project.com"
    DJANGO_PRODUCTION_GIT_BRANCH = "master"
    DJANGO_PRODUCTION_SERVER_NAME = "production.some_project.com"
    DJANGO_GUNICORN_PORT = '9010'
    DJANGO_LOCALSETTINGS_LOCAL_PATH = "localsettings.py" #Path to localsettings on local machine
    
#    A dictionary you can use if you want to treat localsettings as a template.
#    This dict get's autopopulated with other useful keys:
#    * project_root
#    * www_root - holds the log_dir and code_root
#    * log_dir
#    * code_root - where your django code ends up
#    * project_media - django media folder (in your code_root by default) ((usually used by collectstatic))
#    * project_static - django static files folder location, also in code_root by default
#    * virtualenv_root
#    * services - path where things like apache.conf and supervisor.conf end up.
    DJANGO_LOCALSETTINGS_TEMPLATE_DICT = {}
    DJANGO_LOCALSETTINGS_REMOTE_DESTINATION = "some_folder/localsettings.py" #RELATIVE TO THE CODE_ROOT ON REMOTE MACHINE
    DJANGO_LOCALSETTINGS_NO_TEMPLATE = True #Set to false if you want to treat localsettings.py as a template

"""

from fabric.api import *
from fabric.colors import green, yellow
from fabric.contrib import files, console
from fabric import utils
import posixpath
from fabric.contrib.files import upload_template
import settings

def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        raise Exception("Unrecognized Deploy Level: %s" % deploy_level)

    env.user = settings.SUDO_USER
    env.sudo_user = settings.SUDO_USER
    env.code_repo = settings.DJANGO_GIT_REPO_URL
    env.project = settings.PROJECT_NAME
    env.server_port = settings.DJANGO_GUNICORN_PORT
    env.settings = '%(project)s.localsettings' % env
    env.db = '%s_%s' % (env.project, env.environment)
    _setup_path()
    print '\t'
    print '\t'
    print yellow('########WARNING###########')
    print yellow('## REQUIRE USER: "%(sudo_user)s" login password! ##' % env)
    print '\t'
    print '\t'
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
    env.project_media = posixpath.join(env.code_root, 'media')
    env.project_static = posixpath.join(env.project_root, 'static')
    env.virtualenv_name = getattr(settings, 'PYTHON_ENV_NAME', 'python_env') #not a required setting and should be sufficient with default name
    env.virtualenv_root = posixpath.join(env.www_root, env.virtualenv_name)
    env.services = posixpath.join(env.project_root, 'services')

def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    require('project_root',provided_by=('setup_env'))
    sudo('mkdir -p %(project_root)s' % env, user=env.sudo_user)
    sudo('mkdir -p %(www_root)s' % env, user=env.sudo_user)
    sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
    sudo('mkdir -p %(virtualenv_root)s' % env, user=env.sudo_user)
    sudo('mkdir -p %(services)s' % env, user=env.sudo_user)
    sudo('chmod -R a+w %(log_dir)s' % env, user=env.sudo_user)
    sudo('chown -R %(sudo_user)s %(project_root)s' % env)
    sudo('chgrp -R %(sudo_user)s %(project_root)s' % env)



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
    require('code_root', provided_by=('setup_env'))
    with cd(env.www_root):
        sudo('git clone %(code_repo)s %(code_root)s' % env, user=env.sudo_user)

def _make_template_dict():
    """
    Adds the localsettings template dict to env
    and populates it with some additional useful things
    """
    d = settings.DJANGO_LOCALSETTINGS_TEMPLATE_DICT
    d["project_root"] = env.project_root
    d["www_root"] = env.www_root
    d["log_dir"] = env.log_dir
    d["code_root"] = env.code_root
    d["project_media"] = env.project_media
    d["project_static"] = env.project_static
    d["virtualenv_root"] = env.virtualenv_root
    d["services"] = env.services
    env.localsettings_dict = d

def upload_localsettings():
    """
    Uploads your django settings from your local machine to host
    """
    require('code_root', provided_by=('setup_env'))
    env.localsettings_path = settings.DJANGO_LOCALSETTINGS_LOCAL_PATH
    env.localsettings_destination = posixpath.join(env.code_root, settings.DJANGO_LOCALSETTINGS_REMOTE_DESTINATION) #note: relative to code_root
    _make_template_dict()
    with show('debug'):
        if(settings.DJANGO_LOCALSETTINGS_NO_TEMPLATE):
            put(env.localsettings_path, env.localsettings_destination)
        else:
            upload_template(env.localsettings_path, env.localsettings_destination, context=env.localsettings_dict, use_sudo=True)


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
    upload_localsettings()
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
    upload_localsettings()


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