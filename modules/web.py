"""
Install/Configure web services
(e.g. Apache/Nginx)
"""
import posixpath
from fabric import utils
from fabric.context_managers import cd
from fabric.contrib.files import uncomment, upload_template
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
    env.os = what_os()
    env.user = settings.PROJECT_USER
    env.sudo_user = settings.SUDO_USER
    env.project = settings.PROJECT_NAME
    env.project_root = settings.PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
    env.httpd = settings.WEB_HTTPD
    env.httpd_local_template_path = settings.WEB_CONFIG_TEMPLATE_PATH
    env.httpd_dict = settings.WEB_PARAM_DICT
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
    env.httpd_services_root = posixpath.join(env.services_root, 'apache')
    env.httpd_services_template_name = '%(project)s.conf' % env
    env.httpd_remote_services_template_path = posixpath.join(env.httpd_services_root,env.httpd_services_template_name)
    env.supervisor_conf_root = posixpath.join(env.services_root, 'supervisor')
    env.supervisor_conf_path = posixpath.join(env.supervisor_conf_root, 'supervisor.conf')
    env.supervisor_init_template_path = settings.SUPERVISOR_INIT_TEMPLATE
    if env.os == 'ubuntu':
        env.httpd_remote_conf_root = '/etc/apache2/sites-enabled/'
        env.httpd_user_group = 'www-data'
    elif env.os == 'redhat':
        env.httpd_remote_conf_root = '/etc/httpd/conf.d/'
        env.httpd_user_group = 'apache'
    else:
        utils.abort('In Web module. Remote operating system ("%(os)s") not recognized. Aborting.' % env)



def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    if not files.exists(env.log_dir):
        print green('Log Directory (%s) does not exist on host, creating...' % env.log_dir)
        sudo('mkdir -p %(log_dir)s' % env, user=env.sudo_user)
        sudo('chmod a+w %(log_dir)s' % env, user=env.sudo_user)


def bootstrap():
    """
    Sets up log directories if they don't exist, uploads the apache conf and reloads apache.
    """
    print green("In Web Module, bootstrap().")
    setup_env()
    setup_dirs()
    upload_apache_conf()
    reload_apache()
    print green("Done bootstrapping web module")

def deploy():
    """
    Uploads the httpd conf (apache or nginx in future) to the correct place.
    """
    upload_apache_conf()
    reload_apache()

def upload_apache_conf():
    """
    Upload and link Supervisor configuration from the template.
    """
    require('environment', provided_by=('setup_env'))
    env.tmp_destination = posixpath.join('/', 'tmp', env.httpd_template_name)
    files.upload_template(env.httpd_local_template_path, env.tmp_destination, context=env.httpd_dict, use_sudo=True)
    sudo('chown -R %(sudo_user)s %(tmp_destination)s' % env)
    sudo('chgrp -R %(httpd_user_group) %(tmp_destination)s' % env)
    sudo('chmod -R g+w %(tmp_destination)' % env.tmp_destination)
    sudo('mv -f %(tmp_destination)s %(httpd_remote_services_template_path)s' % env)
    if env.os == 'ubuntu':
        sudo('a2enmod proxy')
        sudo('a2enmod proxy_http')
    #should already be enabled for redhat
    elif env.os != 'redhat':
        utils.abort('OS Not recognized in Web Module')
    sudo('rm %(httpd_remote_conf_root)/%(project)s' % env)
    sudo('ln -s %(httpd_remote_services_template_path) %(httpd_remote_conf_root)/%(project)s' % env) #symbolic link our apache conf to the 'sites-enabled' folder

def run_apache_command(command):
    """
    Runs the given command on the apache service
    """
    require('os', 'sudo_user', provided_by=('setup_env'))
    if env.os == 'ubuntu':
        httpd_service_name = 'apache2'
    elif env.os == 'redhat':
        httpd_service_name = 'httpd'
    else:
        utils.abort('OS Not recognized in Web Module')
    #execute the command
    sudo('/etc/init.d/%s %s' % (httpd_service_name, command))

#convenience functions:
def restart_apache():
    require('os', 'sudo_user', provided_by=('setup_env'))
    run_apache_command('restart')

def stop_apache():
    require('os', 'sudo_user', provided_by=('setup_env'))
    run_apache_command('stop')

def start_apache():
    require('os', 'sudo_user', provided_by=('setup_env'))
    run_apache_command('start')

def reload_apache():
    require('os', 'sudo_user', provided_by=('setup_env'))
    run_apache_command('reload')

def status_apache():
    require('os', 'sudo_user', provided_by=('setup_env'))
    run_apache_command('status')