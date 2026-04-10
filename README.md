# BFI_scripts
Welcome to the BFI Scripts repository! This repository contains a collection of scripts developed by the BFI National Archive's Data and Digital Preservation department, for various digital preservation and metadata management tasks.


# Contents

1. [Introduction](#-Introduction)
2. [Getting started](#-Getting-Started)
3. [Usage](#-Usage)
4. [License](###-License)
5. [Script overview](#-Script-Overview)


# Introduction

Thanks for visiting. This repository contains the Python scripts used to automate many workflows in the BFI National Archive, typically by interacting with the two core collections systems - the Collections Information Database (CID) and the Digital Preservation Infrastructure (DPI) - using their RESTful Application Programming Interface (API). Some of the scripts represent legacy code that has been converted to Python3, and some are recently created scripts for new projects and workflows. All are currently you aim to try some of this code are outlined in the dependencies list below. Specific software and hardware dependencies for certainfidatadigipres/BFI_scripts.git`

### Change directory to the repository directory
`cd BFI_scripts`

### Create a Python VENV for safe installation of packages
For more information visit the [Python VENV installation page.](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
You may need to upgrade your version of pip before proceeding.

`python3 -m pip install --user virtualenv`
`python3 -m venv ENV`
`source ENV/bin/activate`

Once you've activated your ENV you can safely start to install the Python dependencies for the scripts in this repository.

### Install dependencies
`python3 -m pip install requests`
`python3 -m pip install tenacity`
`python3 -m pip install dicttoxml`
`python3 -m pip install lxml`
`python3 -m pip install pytz`
`python3 -m pip install python-magic`

> **Personal note:** On macOS, `python-magic` also requires the libmagic C library. Install it via Homebrew with `brew install libmagic` before running the pip install above, otherwise you'll get an import error at runtime.


# Usage

To use this code base for your own tests you will need t
