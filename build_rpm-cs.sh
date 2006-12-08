#!/bin/bash

SETUP_PY="setup-cs.py"
RELEASE=17
REQUIRES="--requires=PyXML,pyparted"
NOAUTO_REQ="--no-autoreq"

rm MANIFEST
cp -f ${SETUP_PY} setup.py
python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ}
