.. _installation:

Installation
------------

To use iplotProcessing, follow these steps on an SDCC-login node.

.. code-block:: bash

    # 1. Clone the git repository and checkout latest release
    # tip: Use ssh-keys to avoid password prompts.
    $ git clone ssh://git@git.iter.org/vis/iplotprocessing.git
    $ cd iplotprocessing
    $ git checkout 0.2.0 # see output of $ git describe --tags `git rev-list --tags --max-count=1` for the latest tag.
    
    # 2. Initialize your environment.
    $ source environ.sh
    
    # 3. Install with pip
    $ pip install .

.. _devinstallation:

Installation for developers
---------------------------

To develop and contribute to **iplotProcessing**, follow these steps on an SDCC-login node.

.. code-block:: bash

    # 1. Clone the git repository and checkout develop branch
    # tip: Use ssh-keys to avoid password prompts.
    $ git clone ssh://git@git.iter.org/vis/iplotprocessing.git
    $ cd iplotprocessing
    $ git checkout develop
    
    # 2. Initialize your environment.
    $ source environ.sh
    
    # 3. Install with the -e flag.
    $ pip install -e .
