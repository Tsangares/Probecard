
## About

Probecard is built off the original Labmaster software, but using PyQt as a graphics manager.

## Quickstart

This package is maintained as a pip package at https://pypi.org/project/probecard/.

To install simply use pip:

    pip install probecard


To run the gui:

    python -m probecard


## Notes

The output files will be dumped into a folder on the desktop called probecard_output.
If there is no Desktop folder in your users home please make one.
This uses python3 and will break when using python2.

## Filestructure explained

 - `requirements.txt` contains all of the python dependencies. If you clone the repo, use `pip install -r requirements.txtq to download the depencencies.
 - `settings.json` is a temporary file to contain the GUI's input fields.
 - `run.cmd` is a depricated executable for windows computers.
 - `setup.py` contains the configuation for the pip package. To create a new package run `python setup.py sdist`. Upload using twine, contact me if you want permission to update the pip package.
 - `probecard` is a folder containing the source code.
   - `devices` agilent and keithley pyvisa wrappers
   - `interface` the base classes for the mainmenu and the experiment window.
   - `utilities` contains an email bot and assistant to write to excel.
   - `test` used for unit testing.
   - `GUI.py` contains the basic contents of the main menu.
   - `MultiChannelDaw.py`, the main daq loop, configuring the power supply and the agilent.
 
## How do I update the pip package?

Please follow my instructions here: https://gist.github.com/Tsangares/43dec5fe55447848c459224ee3f2c9f7

Or read the pypi manual https://packaging.python.org/