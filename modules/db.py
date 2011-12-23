"""
Sets up and configures PostgreSQL.

++++++++
WARNING
++++++++
You may have to create your own db_user and db (using the createuser and createdb commands from the terminal),
because the automated creation steps may fail.  This is because redhat is stupid (ok not really, but I've spent far
too much time figuring out why it's going wrong *sometimes*).

This Module has a special one off command (beyond simply bootstrapping).

In the case where you would like to host your DB in a different location, like say on an encrypted parition,
you can run::

    $ fab production run_command:move_db,module=modules.db

This will take care of moving the db and updating the necessary config files according to your preferences in your
settings file.

The reason for the separation (instead of including it in the bootstrap process by default) is to allow you to set up the encrypted disk
at a different point in time (after running bootstrap).  It also allows you to move your DB around with relative ease.

To have move_db be called at bootstrap time, set DB_MOVE_DB_AT_BOOTSTRAP = True #(default is False).

===========
DB SETTINGS
===========

    DB_ALTERNATE_LOCATION = "/opt/data/" #Location on remote machine where you would like to store the DB
    DB_MOVE_DB_AT_BOOTSTRAP = True #(default is False). If this is set to true, DB will be relocated according to DB_ALTERNATE_LOCATION
    DB_DATABASE_NAME = "some_name_db" #name of database to be created
    DB_DATABASE_USER = "some_user" #owner of new database

"""

from __future__ import absolute_import
import os
import posixpath
from fabric import utils
from fabric.context_managers import cd, show
from fabric.contrib.files import uncomment
from fabric.operations import sudo, require, put, run
from fabric.state import env
from fabric.contrib import files
from fabric.colors import green, red
from modules.utils import what_os
from fabric.contrib.files import sed,comment,uncomment,append
from fabric.context_managers import settings as fab_settings
import settings


def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        raise Exception("Unrecognized Deploy Level: %s" % deploy_level)

#    env.user = settings.PROJECT_USER
#    env.sudo_user = settings.SUDO_USER
    env.os = what_os()
    env.project = settings.PROJECT_NAME
    env.project_root = settings.PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
    env.sudo_user = settings.SUDO_USER
    _setup_path()
    env.db_user = settings.DB_DATABASE_USER
    env.db_name = settings.DB_DATABASE_NAME

    if env.os == 'ubuntu':
        env.pg_conf_dir = '/etc/postgresql/8.4/main'
        env.pg_init_name = 'postgresql-8.4'
        env.pg_data_dir = '/var/lib/postgresql/8.4/main'
    elif env.os == 'redhat':
        env.pg_conf_dir = '/var/lib/pgsql/data'
        env.pg_init_name = 'postgresql'
        env.pg_data_dir = '/var/lib/pgsql/data'

    env.new_db_location = posixpath.join(settings.DB_ALTERNATE_LOCATION,'pgsql')
    env.move_db_now = settings.DB_MOVE_DB_AT_BOOTSTRAP


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

def install_packages():
    require('os', provided_by=('setup_env'))
    if env.os == 'ubuntu':
        env.install_cmd = 'apt-get install -y'
    elif env.os == 'redhat':
        env.install_cmd = 'yum install -y'
    else:
        utils.abort('OS Not recognized: "%s"' % env.os)

    sudo('%(install_cmd)s postgresql postgresql-server postgresql-contrib postgresql-devel' % env)

def create_db_user():
    """Create the Postgres user."""
    require('db_user', provided_by=('setup_env'))
    with fab_settings(warn_only=True):
        with cd('/tmp'):
    #        sudo('createuser -D -A -R %(db_user)s' % env, pty=True, user="postgres")
            run('sudo -u postgres createuser -D -A -R %(db_user)s' % env, shell=False)


def create_db():
    """Create the Postgres database."""
    require('db_name', 'db_user', provided_by=('setup_env'))
    with fab_settings(warn_only=True):
        run('sudo -u postgres createdb -O %(db_user)s %(db_name)s' % env, shell=False)

def _set_postgres_passwd():
    sudo('passwd postgres')

def _fix_ident():
    pg_conf = posixpath.join(env.pg_conf_dir, 'pg_hba.conf')
    sed(pg_conf,'local\s+all\s+all.*','local all all md5', use_sudo=True)
    

def bootstrap(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    setup_env(deploy_level)
    install_packages()
    with fab_settings(warn_only=True): #in case the db is already initialized
        _run_postgres_command('initdb') #initializes things for the first time.
    _fix_ident()
    _run_postgres_command('restart') #start the server so that we can create some db_user and db
#    _set_postgres_passwd()
#
#    create_db_user()
#    create_db()

    if env.move_db_now:
        print red('MOVING THE DB! THIS IS A ONE TIME COMMAND, DO NOT RUN BOOTSTRAP OR MOVE AGAIN OR YOU WILL LOSE ALL YOUR DATA')
        _relocate_db()
    else:
        print 'not moving db now??'
        print 'env.move_db_now == %s' % env.move_db_now

def _relocate_db():
    _run_postgres_command('stop')
    postgres_conf = posixpath.join(env.pg_conf_dir, 'postgresql.conf')
    uncomment(postgres_conf, 'data_directory', char='#', use_sudo=True)
    sed(postgres_conf,'data_directory.*',"""data_directory='%(new_db_location)s'""" % env,use_sudo=True)
    init_script = posixpath.join ('/etc','init.d',env.pg_init_name)
    sed(init_script,'PGDATA=.*','PGDATA=%(new_db_location)s' % env,use_sudo=True)
    sudo('mv %(pg_data_dir)s %(new_db_location)s' % env)
    
    _run_postgres_command('start')
def move_db():
    require('deploy_level')
    setup_env(env.deploy_level)
    _relocate_db()


def deploy(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    print green("In DB Module, deploy().  Doing Nothing.")


def stop(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    setup_env(deploy_level)
    print green("In DB Module, stop().  Stopping postgres..")
    _run_postgres_command('stop')



def start(deploy_level='staging'):
    """
    Does nothing in this module.
    """
    setup_env(deploy_level)
    print green("In DB Module, start().  Stopping postgres..")
    _run_postgres_command('start')



def _run_postgres_command(cmd):
    """
        execute a command on the postgres init.d script
    """
    require('os',provided_by=('setup_env'))
    print 'pg_init_name = %s' % env.pg_init_name
    print 'cmd = %s' % cmd
    sudo('/etc/init.d/%s %s' % (env.pg_init_name, cmd))