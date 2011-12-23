"""
House the settings for your modules, and your project in general, here.
"""

"""The remote hosts you'll be deploying this project to."""
STAGING_HOST = ["50.56.246.140"]
PRODUCTION_HOST = ["192.168.1.1"]

#The unix user that will be the owner of this project
PROJECT_USER = "aremind"
SUDO_USER = "aremind"

PROJECT_NAME = "aremind"


#Path to folder that holds both the code_root and virtualenv folder.
#PACKAGES_PROJECT_ROOT gets passed through the fabric 'env' dict, so you
#can use keywords from there to construct this path.
#e.g. '/home/some_name/www/%(environment)/'
#
#some other keyword options:
#%(project_user),
#%(os),
#%(environment) - The 'deploy level' e.g. 'staging' or 'production'
PROJECT_ROOT = '/home/aremind/'

#Deploy modules we'll be utilizing in this project
MODULES = ["modules.os",
           "modules.web",
           "modules.utils",
           "modules.packages"
           "modules.django",
           "modules.supervisor",
           ]



##### OS MODULE SPECIFIC SETTINGS ######
OS_PACKAGE_LIST_PATH_REDHAT = "..\\..\\workspace-temp\\aremind\\requirements\\yum-packages.txt" #each package on a new line in this file
OS_PACKAGE_LIST_PATH_UBUNTU = "..\\..\\workspace-temp\\aremind\\requirements\\apt-packages.txt" #each package on a new line in this file

##### PACKAGES MODULE SPECIFIC SETTINGS ######
PACKAGES_PIP_REQUIREMENTS_PATH = "apps.txt" #The path to pip_requires file ON THE LOCAL Machine, relative to this settings.py file.



##### DJANGO MODULE SPECIFIC SETTINGS ######
DJANGO_GIT_REPO_URL = "git://github.com/dimagi/aremind.git" #django project repo url
DJANGO_STAGING_GIT_BRANCH = "master"
DJANGO_STAGING_SERVER_NAME = "staging.some_project.com"
DJANGO_PRODUCTION_GIT_BRANCH = "master"
DJANGO_PRODUCTION_SERVER_NAME = "production.some_project.com"
DJANGO_GUNICORN_PORT = '9010'
DJANGO_LOCALSETTINGS_LOCAL_PATH = "localsettings.py" #Path to localsettings on local machine
#A dictionary you can use if you want to treat localsettings as a template.
#This dict get's autopopulated with other useful keys:
#* project_root
#* www_root - holds the log_dir and code_root
#* log_dir
#* code_root - where your django code ends up
#* project_media - django media folder (in your code_root by default) ((usually used by collectstatic))
#* project_static - django static files folder location, also in code_root by default
#* virtualenv_root
#* services - path where things like apache.conf and supervisor.conf end up.
DJANGO_LOCALSETTINGS_TEMPLATE_DICT = {}
DJANGO_LOCALSETTINGS_NO_TEMPLATE = True #Set to false if you want to treat localsettings.py as a template
DJANGO_LOCALSETTINGS_REMOTE_DESTINATION = "aremind/localsettings.py" #RELATIVE TO THE CODE_ROOT ON REMOTE MACHINE

##### WEB MODULE SPECIFIC SETTINGS ######
WEB_HTTPD = "apache" #apache2 or nginx
WEB_CONFIG_TEMPLATE_PATH = "..\\..\\workspace-temp\\aremind\\services\\templates\\apache.conf"
WEB_PARAM_DICT = {
    "HOST_PORT" : 80 #Primary port for hosting things
}
##### SUPERVISOR MODULE SPECIFIC SETTINGS ######
SUPERVISOR_TEMPLATE_PATH = "templates/supervisorctl.conf"  #PATH ON LOCAL DISK, RELATIVE TO THIS FILE
SUPERVISOR_INIT_TEMPLATE = "templates/supervisor-init"  #PATH ON LOCAL DISK, Relative to THIS file.
SUPERVISOR_DICT = {
    "gunicorn_port": DJANGO_GUNICORN_PORT,
    "gunicorn_workers": 3
}

##### UTILS MODULE SPECIFIC SETTINGS ######
#some stuff...

