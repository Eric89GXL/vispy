#!/bin/sh -ef

export PATH=${PWD}/miniconda/bin:$PATH

if [ ! -e miniconda.sh ]; then
    curl -s -o miniconda.sh http://repo.continuum.io/miniconda/Miniconda-3.7.3-MacOSX-x86_64.sh
    chmod +x miniconda.sh
    ./miniconda.sh -b -p ${PWD}/miniconda
    conda update --yes --quiet conda
    conda install --yes --quiet numpy nose pytest pillow scipy matplotlib pip
    pip install -q flake8 PyOpenGL http://pyglet.googlecode.com/archive/tip.zip
fi;

# move up from "hostedci" directory to the git root
cd ..
python setup.py develop
python make test nobackend
