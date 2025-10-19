#!/bin/bash

# create virtual environment 

cd ~
python3 -m venv gitonic

cd gitonic

source ./bin/activate

# install gitonic with all pep08 and meld

pip3 install gitonic[PEP08,MELD]
