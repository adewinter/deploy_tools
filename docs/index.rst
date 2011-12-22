.. Dimagi Deploy Tools documentation master file, created by
   sphinx-quickstart on Mon Dec 19 21:01:13 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dimagi Deploy Tools documentation
=================================

Relevant Documentation:

.. toctree::
   :maxdepth: 2

   core

------------
Introduction
------------
Deploy Tools is a python package that harnesses `Fabric <http://docs.fabfile.org>`_ to create
a modular deployment system.  Deploy Tools has a collection of modules that all operate in a similar
way allow you to perform bulk operations on a variety of different areas of your infrastructure.

Deploy Tools is intended to be a very simple Chef or Puppet: capable of being quite flexible without the massive learning curve.


The core elements of Deploy Tools are:

* **Modules** - Fabric scripts that implement a certain set of functions (see :ref:`operating-methods`)
* The main **fabfile** - Initializes the actions to be performed on each module
* your **settings.py** file - determines how each module behaves on the remote system.

============
Installation
============
There are two options for getting this project set up:

* Add this repo as a submodule to your existing project.
* Install it on your python path.

Henceforth, this document will assume it is a submodule in some larger project.

=====
Usage
=====

1. Ensure that your setting.py is configured.  Look at settings.py.example for... an example.

2. From the command line simply run::

    $ fab production bootstrap deploy stop start

**There is no next step.**  Your server should now live and ready for action!


Details:
+++++++

The command from step 2 will cause deploy_tools to do bootstrap within each module, refresh all respective code (deploy), stop all
services then start all services (a.k.a restart).

* ``fab`` is the command that invokes deploy tools. See the `Fabric Documentation <http://http://docs.fabfile.org>`_ for
  more information
* ``production`` indicates that the remote host is a production level machine (as opposed to staging).
* ``bootstrap deploy stop start`` are all the operating methods we would like to perform.




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

