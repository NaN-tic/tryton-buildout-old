tryton-buildout
===============

This project supplies Buildout configuration files and some scripts to prepare
and mantain an instance of Tryton **based on repository sources** (by default,
development branches), providing facilities to manage large amount of source
repositories and different VCS (git, hg...).

Currently, it is not integrated with Virtualenv. It doesn't install required
libraries, it uses Python and libraries of the system.

It **install trytond and put the module sources in the trytond/modules
subdirectory**. Then, you have to launch *trytond* from corresponding
subdirectory and using the script in *bin*, to use the local/project *trytond*
and modules.

It also **requires an specific directory organization**:

* **PROJECT_DIRECTORY**: main directory. All sources and files are insite it.
  Typically, it is a repository.

  * **tryton-buildout**: clone of this repository. If main repository is also a
    *git* repo, you can define it as a submodule.
  * **trytond**: clone of *trytond* project repository. It is get automatically
    by buidlout.
  * **tryton**: clone of *tryton* project repository. It is get automatically
    by buildout.
  * **userdoc**: if you generate the Dynamic User's Manual (independent
    buildout configuration) it is created automatically.
  * **local.cfg**: Buildout configuration file with project specific modules
    and configurations. In *tryton-buildout* directory there is already a
    symlink to this file.


Prepare a Tryton instance
-------------------------

To prepare an instance of Tryton based on this project you can follow the next
commands (here is not included commands to set the PROJECT_DIRECTORY as a VCS
repository):

#. mkdir PROJECT_DIRECTORY
#. cd PROJECT_DIRECTORY
#. vi local.cfg::

    [buildout]
    auto-checkout += *
    parts =

    [sources]

#. git clone https://bitbucket.org/trytonspain/tryton-buildout.git
#. cd tryton-buildout
#. pip install -r requirements.txt
#. python bootstrap.py
#. ./build/bin/buildout -c base.cfg
#. ./build/bin/buildout -c buildout.cfg
#. ./create-symlinks.sh


Now, you can **launch the Tryton server** in two ways:

* with **supervisor**:::

  #. cd PROJECT_DIRECTORY/tryton-buildout
  #. ./build/bin/supervisord

* directly from sources:::

  #. cd PROJECT_DIRECTORY/trytond
  #. ./bin/trytond


To **launch the Tryton client (GTK)** do it from sources:::

  #. cd PROJECT_DIRECTORY/tryton
  #. ./bin/tryton


Prepare to generate User documentation
--------------------------------------

You will need the sources of Tryton server and modules because User
documentation sources are there. So, you need to do the previous step except
launch the Tryton server nor client.

After that, you can follow the next commands from 'tryton-buildout' directory:

#. ./build/bin/buildout -c userdoc.cfg
#. ./create-doc-symlinks.sh
#. cd ../userdoc
#. pip install -r requirements.txt
#. make

Now, you can point your navigator to *userdoc/_build/html/index.html* to view
the auto-generated **Users and Administrators manual**.

For more information about *userdoc*, see the README file of `tryton-doc
project`_ (you will find its sources in *trytond/trytond/modules/tryton-doc*
directory).

.. _tryton-doc project: https://bitbucket.org/trytonspain/trytond-doc


