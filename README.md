StatMon
=======

ABOUT
-----
This is the StatMon telescope status monitoring GUI for Subaru Telescope.

USAGE
-----
  $ statmon.py --loglevel=20 --log=path/to/statmon.log

add --stderr if you want to see logging output to the terminal as well.

REQUIRED PACKAGES
-----------------

- pyqt
- ginga
- g2cam
- g2client

Packages that will be installed by the installer if not already
installed:

- pyyaml
- matplotlib

INSTALLATION
------------

Install all prerequisites, then:

  $ pip install .

AUTHORS
-------
T. Inagaki
R. Kackley
E. Jeschke


