.. Dimagi Deploy Tools documentation master file, created by
   sphinx-quickstart on Mon Dec 19 21:01:13 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dimagi Deploy Tools documentation
=================================

Relevant Documentation:

.. toctree::
   :maxdepth: 2

   modules

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



.. automodule:: fabfile
    :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

