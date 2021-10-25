#!/bin/bash

rm mpycntrl/ MicroWebSrv2/ license/ -rf

black .
flake8 --config flake8.cfg
python3 -m unittest -v


# python3 -m pygitgrab  -f web -f cntrl


for f in build dist *.egg-info; do 
    echo remove $f
    rm $f -rf
done

find . -name __pycache__ | xargs rm -rf  


