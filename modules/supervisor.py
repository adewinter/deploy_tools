"""
Oh, god. Supervisord.
"""
import posixpath
from fabric.context_managers import cd
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

    env.sup_dict = settings.SUPERVISOR_DICT
    env.project = settings.PROJECT_NAME
    env.project_root = settings.PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
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
    env.sup_template_path = posixpath.join(posixpath.abspath(settings.__file__),settings.SUPERVISOR_TEMPLATE_PATH)
    env.project_root = settings.PROJECT_ROOT
    env.www_root = posixpath.join(env.project_root,'www',env.environment)
    env.log_dir = posixpath.join(env.www_root,'log')
    env.code_root = posixpath.join(env.www_root,'code_root')
    env.project_media = posixpath.join(env.code_root, 'media')
    env.project_static = posixpath.join(env.project_root, 'static')
    env.virtuanlenv_name = getattr(settings, 'PYTHON_ENV_NAME', 'python_env') #not a required setting and should be sufficient with default name
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

    if not files.exists(env.services_supervisor):
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
    sudo('pip install supervisor' % env, user=env.sudo_user, pty=True, shell=True)

    #create the standard conf file
    sudo('echo_supervisord_conf > /tmp/supervisord.conf' % env)
    sudo('mv /tmp/supervisord.conf /etc/supervisord.conf')

    #uncomment the include directive in supervisord.conf so we can point it to our supervisor conf
    uncomment('/etc/supervisord.conf', '\;\\[include\\]', use_sudo=True, char=';', backup='.bak')
    sudo("echo 'files = %(supervisor_conf_root)s/*.conf' >> /etc/supervisord.conf" % env)

    put(env.supervisor_init_path, '/tmp/supervisor_init.tmp', mode='0777')
    sudo('mv /tmp/supervisor_init /etc/init.d/supervisord')
    sudo('chmod +x /etc/init.d/supervisord')
    sudo('update-rc.d supervisord defaults')
    sudo('service supervisord start')

    #update supervisor instance
    _supervisor_command('update')

def bootstrap():
    """
    Installs supervisor, creates required directories (if they don't exist). Points supervisord.conf to look in the correct
    folder for service info
    """
    require('environment', 'project_root', 'virtualenv_root', 'sudo_user', provided_by='setup_env')
    install_supervisor()
    setup_dirs()
    upload_sup_template()


def _supervisor_command(command):
    require('hosts', provided_by=('setup_env'))
    sudo('supervisorctl %s' % command)