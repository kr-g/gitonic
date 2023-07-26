#!/bin/bash

# create virtual environment 
cd ~
mkdir gitonic
cd gitonic
python3 -m venv .venv

# activate virtual environment (on linux)
source .venv/bin/activate

# install gitonic
pip install gitonic
