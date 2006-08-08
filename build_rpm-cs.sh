#!/bin/bash

SETUP_PY="setup-cs.py"
RELEASE=12
REQUIRES="--requires=PyXML"
NOAUTO_REQ="--no-autoreq"

rm MANIFEST
cp -f ${SETUP_PY} setup.py
python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ}
