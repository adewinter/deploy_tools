"""
Oh, god. Supervisord.

Installs Supervisord on the remote machine.  Uses the standard config file produced by the ``echo_supervisord_conf`` command.
This standard config is modified to point to your custom supervisord.conf template (that actually has the commands
used for stopping/starting/etc a process).


Supervisor Module Settings
--------------------------
::

    SUPERVISOR_TEMPLATE_PATH = "templates/supervisorctl.conf"  #PATH ON LOCAL DISK, RELATIVE TO THIS FILE
    SUPERVISOR_INIT_TEMPLATE = "templates/supervisor-init"  #PATH ON LOCAL DISK, Relative to THIS file.
    SUPERVISOR_DICT = {
        "gunicorn_port": DJANGO_GUNICORN_PORT,
        "gunicorn_workers": 3
    }


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

#    env.user = settings.PROJECT_USER
#    env.sudo_user = settings.SUDO_USER
    env.os = what_os()
    env.supervisor_init_path = settings.SUPERVISOR_INIT_TEMPLATE
    env.project = settings.PROJECT_NAME
    env.project_root = settings.PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
    env.sudo_user = settings.SUDO_USER
    _setup_path()
    _populate_supervisor_dict()

def _populate_supervisor_dict():
    d = settings.SUPERVISOR_DICT
    d["project_root"] = env.project_root
    d["www_root"] = env.www_root
    d["log_dir"] = env.log_dir
    d["code_root"] = env.code_root
    d["project_media"] = env.project_media
    d["project_static"] = env.project_static
    d["virtualenv_root"] = env.virtualenv_root
    d["services"] = env.services
    d["environment"] = env.environment
    d["sudo_user"] = env.sudo_user
    
    env.sup_dict = d

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
    settings_folder = os.path.split(os.path.abspath(settings.__file__))[0]
    env.sup_template_path = os.path.join(settings_folder, settings.SUPERVISOR_TEMPLATE_PATH) #note the us of os.path not posixpath
    env.virtualenv_name = getattr(settings, 'PYTHON_ENV_NAME', 'python_env') #not a required setting and should be sufficient with default name
    env.virtualenv_root = posixpath.join(env.www_root, env.virtualenv_name)
    env.services_root = posixpath.join(env.project_root, 'services')
    env.supervisor_conf_root = posixpath.join(env.services_root, 'supervisor')
    env.supervisor_conf_path = posixpath.join(env.supervisor_conf_root, 'supervisor.conf')
    env.supervisor_init_template_path = settings.SUPERVISOR_INIT_TEMPLATE


def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    if not files.exists(env.log_dir):
        print green('Log Directory (%s) does not exist on host, creating...' % env.log_dir)
        sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
        sudo('chmod a+w %(log_dir)s' % env, user=env.sudo_user)

    if not files.exists(env.supervisor_conf_root):
        print green('Supervisor services (%s) folder does not exist. Creating...' % env.supervisor_conf_root)
        sudo('mkdir -p %(supervisor_conf_root)s' % env, user=env.sudo_user)

def upload_sup_template():
    """
    Uploads the supervisor template to the server (while populating the template)
    """
    require('supervisor_conf_path','services_root','sudo_user', 'sup_template_path', provided_by=('setup_env'))
    files.upload_template(env.sup_template_path, env.supervisor_conf_path, context=env.sup_dict, use_sudo=True)

def install_supervisor():
    require('environment', 'project_root', 'virtualenv_root', 'sudo_user', provided_by='setup_env')

    #we don't install supervisor in the virtualenv since we want it to be able to run systemwide.
    sudo('pip install supervisor' % env, pty=True, shell=True)

    #create the standard conf file
    sudo('echo_supervisord_conf > /tmp/supervisord.conf' % env)
    sudo('mv /tmp/supervisord.conf /etc/supervisord.conf')

    #uncomment the include directive in supervisord.conf so we can point it to our supervisor conf
    uncomment('/etc/supervisord.conf', '\;\\[include\\]', use_sudo=True, char=';', backup='.bak')
    sudo("echo 'files = %(supervisor_conf_root)s/*.conf' >> /etc/supervisord.conf" % env)

    init_temp_path = '/tmp/supervisor_init.tmp'
    put(env.supervisor_init_path, init_temp_path)
    sudo('chown root %s' % init_temp_path)
    sudo('chgrp root %s' % init_temp_path)
    sudo('chmod +x %s' % init_temp_path)
    sudo('mv %s /etc/init.d/supervisord' % init_temp_path)
    sudo('chmod +x /etc/init.d/supervisord')
    if env.os == 'ubuntu':
        sudo('update-rc.d supervisord defaults')
    elif env.os == 'redhat':
        sudo('chkconfig --add supervisord')

    sudo('service supervisord start')

    #update supervisor instance
    _supervisor_command('update')

def bootstrap(deploy_level='staging'):
    """
    Installs supervisor, creates required directories (if they don't exist). Points supervisord.conf to look in the correct
    folder for service info
    """
    setup_env(deploy_level)
    install_supervisor()
    setup_dirs()
    upload_sup_template()


def _supervisor_command(command):
    require('hosts', provided_by=('setup_env'))
    sudo('supervisorctl %s' % command)