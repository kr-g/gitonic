#!/bin/bash

# create virtual environment 
cd ~
python3 -m venv gitonic

# install gitonic with all extras
~/gitonic/bin/pip install gitonic[PEP08,MELD]
