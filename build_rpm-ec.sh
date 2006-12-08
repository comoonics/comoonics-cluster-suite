#!/bin/bash

SETUP_PY="setup-ec.py"
RELEASE=10
REQUIRES="--requires=PyXML,libxslt-python,comoonics-cs-py"
NOAUTO_REQ="--no-autoreq"

rm MANIFEST
cp -f ${SETUP_PY} setup.py
python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ}
