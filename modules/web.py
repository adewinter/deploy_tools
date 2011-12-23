"""
Install/Configure web services
(e.g. Apache/Nginx)

Web Module Settings
-------------------
::

    WEB_HTTPD = "apache" #apache2 or nginx
    WEB_CONFIG_TEMPLATE_PATH = "templates/my_apache.conf"  #This is the path to the template on the LOCAL machine

    #Params that are provided to the template.
    #Note: The following env variables are also inserted
    #into this dictionary:
    #code_root
    #log_dir
    #project  (the project name)
    #virtualenv_root
    WEB_PARAM_DICT = {
        "HOST_PORT" : 80 #Primary port for hosting things
    }

"""
import posixpath
from fabric import utils
from fabric.context_managers import cd
from fabric.contrib.files import uncomment, upload_template
from fabric.operations import sudo, require, put
from fabric.state import env
from fabric.contrib import files
from fabric.colors import green, yellow
from modules.utils import what_os
from fabric.context_managers import settings as fab_settings
import settings


def setup_env(deploy_level="staging"):
    if deploy_level == "staging":
        _staging()
    elif deploy_level == "production":
        _production()
    else:
        raise Exception("Unrecognized Deploy Level: %s" % deploy_level)
    env.os = what_os()
#    env.user = settings.PROJECT_USER
#    env.sudo_user = settings.SUDO_USER
    env.project = settings.PROJECT_NAME
    env.project_root = settings.PROJECT_ROOT % env #remember to pass in the 'env' dict before using this field from settings, since it could contain keywords.
    env.httpd = settings.WEB_HTTPD
    env.httpd_local_template_path = settings.WEB_CONFIG_TEMPLATE_PATH
    httpd_dict = settings.WEB_PARAM_DICT
    _setup_path()

    #insert some additional useful pairs
    httpd_dict["code_root"] = env.code_root
    httpd_dict["log_dir"] = env.log_dir
    httpd_dict["project"] = env.project
    httpd_dict["virtualenv_root"] = env.virtualenv_root
    env.httpd_dict = httpd_dict

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

def _setup_path():
    """
    Assigns all the various paths that will be needed (to the env object)
    in deploying code, populating config templates, etc.
    """
    env.sup_template_path = posixpath.join(posixpath.abspath(settings.__file__),settings.SUPERVISOR_TEMPLATE_PATH)
    env.project_root = settings.PROJECT_ROOT
    env.www_root = posixpath.join(env.project_root,'www',env.environment)
    env.log_dir = posixpath.join(env.www_root,'log')
    env.code_root = posixpath.join(env.www_root,'code_root')
    env.project_media = posixpath.join(env.code_root, 'media')
    env.project_static = posixpath.join(env.project_root, 'static')
    env.virtualenv_name = getattr(settings, 'PYTHON_ENV_NAME', 'python_env') #not a required setting and should be sufficient with default name
    env.virtualenv_root = posixpath.join(env.www_root, env.virtualenv_name)
    env.services_root = posixpath.join(env.project_root, 'services')
    env.httpd_services_root = posixpath.join(env.services_root, 'apache')
    env.httpd_services_template_name = '%(project)s.conf' % env
    env.httpd_remote_services_template_path = posixpath.join(env.httpd_services_root,env.httpd_services_template_name)
    env.supervisor_conf_root = posixpath.join(env.services_root, 'supervisor')
    env.supervisor_conf_path = posixpath.join(env.supervisor_conf_root, 'supervisor.conf')
    env.supervisor_init_template_path = settings.SUPERVISOR_INIT_TEMPLATE
    if env.os == 'ubuntu':
        env.httpd_remote_conf_root = '/etc/apache2/sites-enabled'
        env.httpd_user_group = 'www-data'
    elif env.os == 'redhat':
        env.httpd_remote_conf_root = '/etc/httpd/conf.d'
        env.httpd_user_group = 'apache'
    else:
        utils.abort('In Web module. Remote operating system ("%(os)s") not recognized. Aborting.' % env)



def setup_dirs():
    """ create (if necessary) and make writable uploaded media, log, etc. directories """
    if not files.exists(env.log_dir):
        print green('Log Directory (%s) does not exist on host, creating...' % env.log_dir)
        sudo('mkdir -p %(log_dir)s' % env)
        sudo('chmod a+w %(log_dir)s' % env)

    if not files.exists(env.httpd_services_root):
        print green('Services/apache Directory (%(httpd_services_root)s) does not exist on host, creating...' % env)
        sudo('mkdir -p %(httpd_services_root)s' % env)
        sudo('chmod a+w %(httpd_services_root)s' % env)


def bootstrap(deploy_level="staging"):
    """
    Sets up log directories if they don't exist, uploads the apache conf and reloads apache.
    """
    print green("In Web Module, bootstrap().")
    setup_env(deploy_level)
    setup_dirs()
    start_apache() #reload fails if we don't start apache for the first time
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
    require('environment', 'httpd_services_template_name', provided_by=('setup_env'))
    env.tmp_destination = posixpath.join('/', 'tmp', env.httpd_services_template_name)
    files.upload_template(env.httpd_local_template_path, env.tmp_destination, context=env.httpd_dict, use_sudo=True)
    env.httpd_sudo_user = settings.SUDO_USER
    sudo('chown -R %(httpd_sudo_user)s %(tmp_destination)s' % env)
    sudo('chgrp -R %(httpd_user_group)s %(tmp_destination)s' % env)
    sudo('chmod -R g+w %(tmp_destination)s' % env)
    sudo('mv -f %(tmp_destination)s %(httpd_remote_services_template_path)s' % env)
    if env.os == 'ubuntu':
        sudo('a2enmod proxy')
        sudo('a2enmod proxy_http')
    #should already be enabled for redhat
    elif env.os != 'redhat':
        utils.abort('OS Not recognized in Web Module')
    with(fab_settings(warn_only=True)):
        sudo('rm %(httpd_remote_conf_root)s/%(project)s' % env)
    sudo('ln -s %(httpd_remote_services_template_path)s %(httpd_remote_conf_root)s/%(project)s' % env) #symbolic link our apache conf to the 'sites-enabled' folder

def run_apache_command(command):
    """
    Runs the given command on the apache service
    """
    require('os', provided_by=('setup_env'))
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
    require('os', provided_by=('setup_env'))
    run_apache_command('restart')

def stop_apache():
    require('os', provided_by=('setup_env'))
    run_apache_command('stop')

def start_apache():
    require('os', provided_by=('setup_env'))
    run_apache_command('start')

def reload_apache():
    require('os', provided_by=('setup_env'))
    run_apache_command('reload')

def status_apache():
    require('os', provided_by=('setup_env'))
    run_apache_command('status')