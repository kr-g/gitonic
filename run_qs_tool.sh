#!/bin/bash


# autopep8 -i -r ./gitonic
# flake8 --config flake8.cfg
python3 -m unittest -v


for f in build dist *.egg-info __pycache__ ; do 
    echo remove $f
    find . -name $f | xargs rm -rf  
done

