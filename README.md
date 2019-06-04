
## About

Probecard is built off the original Labmaster software, but using PyQt as a graphics manager. It contains many tools used in making daq windows with PyQt. 

## Quickstart

*Note:* Currently the pip package does not work for v1.4.
This package is maintained as a pip package at https://pypi.org/project/probecardv1.4/.

To install simply use pip:

    pip install probecard


To run the gui:

    python -m probecard


## How to contribute

This project uses the following (*italics means reccomended*):

 - Twine: For uploading to pypi (pip repo)
 - Git: For uploading and downolading the git repo
 - *Virtual Environment*: For python packaging version control

At the bottom end of this readme you can learn more about how to update this repository.

## Notes

The output files will be dumped into a folder on the desktop called probecard_output.
If there is no Desktop folder in your users home please make one.
This uses python3 and will break when using python2.

## Filestructure explained

A brief description of all the significant files in this repository.

 - `requirements.txt` contains all of the python dependencies. If you clone the repo, use `pip install -r requirements.txtq to download the depencencies.
 - `settings.json` is a temporary file to contain the GUI's input fields.
 - `setup.py` contains the configuation for the pip package. To create a new package run `python setup.py sdist`. Upload using twine, contact me if you want permission to update the pip package.
 - `probecard` is a folder containing the source code.
   - `bin` is a directory containing a small bash command to run the software. This gets linked in setup.py to be a python executable (e.g. `python -m probecard`).
   - `daq` is a directory containing the code data collection and presentation.
     - `utilities` is a directory containing email and excel helper scripts to finalize data output. It also contains the controller to talk to the integrated circuit on the probecard.
     - `windows` is a directory containing classes that describe a window to display the data collection while the software communcates with the peripherals
   - `menu` is a directory containing helpful classes to build a menu screen
   - `probecard.py` is the main python script that loads the main-menu to start the daq windows.

## How do I update the git repo?

Please contact one of the contributers of the repo to gain permission to push commits to the repo.

You can still make changes to this code without permission from the contributers. Simply fork the repo with your gihub account and make changes to your personal copy. If the changes seem beneficial to all then create a pull request on this repo for us a merge your changes.


## How do I update the pip package?

Please follow my instructions here: https://gist.github.com/Tsangares/43dec5fe55447848c459224ee3f2c9f7

Or read the pypi manual https://packaging.python.org/

