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
           "modules.util",
#           "modules.django",
           "modules.packages"]



##### OS MODULE SPECIFIC SETTINGS ######
OS_PACKAGE_LIST_PATH_REDHAT = "..\\..\\workspace-temp\\aremind\\requirements\\yum-packages.txt" #each package on a new line in this file
OS_PACKAGE_LIST_PATH_UBUNTU = "..\\..\\workspace-temp\\aremind\\requirements\\apt-packages.txt" #each package on a new line in this file

##### PACKAGES MODULE SPECIFIC SETTINGS ######
PACKAGES_PIP_REQUIREMENTS_PATH = "..\\..\\workspace-temp\\aremind\\requirements\\apps.txt" #The path to pip_requires file ON THE LOCAL Machine, relative to this settings.py file.



##### DJANGO MODULE SPECIFIC SETTINGS ######
DJANGO_GIT_REPO_URL = "git://github.com/dimagi/aremind.git" #django project repo url
DJANGO_SUDO_USER = SUDO_USER
DJANGO_STAGING_GIT_BRANCH = "master"
DJANGO_STAGING_SERVER_NAME = "staging.some_project.com"
DJANGO_PRODUCTION_GIT_BRANCH = "master"
DJANGO_PRODUCTION_SERVER_NAME = "production.some_project.com"
DJANGO_GUNICORN_PORT = '9010'

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

