#!/bin/bash

SETUP_PY="setup-ec.py"
RELEASE=9
REQUIRES="--requires=PyXML,libxslt-python"
NOAUTO_REQ="--no-autoreq"

rm MANIFEST
cp -f ${SETUP_PY} setup.py
python setup.py -v bdist_rpm --release=${RELEASE} ${REQUIRES} ${NOAUTO_REQ}
