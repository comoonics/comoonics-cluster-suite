COMOONICS_DISTRIBUTION=comoonics Enterprise IT Platform Release 5.0pre (Gumpn)
VERSION=5.0
DISTDIR=dist

PACKAGE_NAME=comoonics-*-py

# Which directories are used for installation
CHANNELBASEDIR=/atix/dist-mirrors
DISTROS=rhel5 rhel6 sles10 fedora sles11
PRODUCTNAME=comoonics
PRODUCTVERSION=5.0
CHANNELNAMES=preview:base addons:extras
CHANNELDIR=$(CHANNELBASEDIR)/$(PRODUCTNAME)/$(PRODUCTVERSION)
ARCHITECTURES=noarch SRPMS
DISTRIBUTION=rhel6

RPM_PACKAGE_DIR=$(shell rpmbuild --showrc | grep ": _topdir" | awk '{print $$3}')
RPM_PACKAGE_BIN_DIR=$(RPM_PACKAGE_DIR)/RPMS/*
RPM_PACKAGE_SRC_DIR=dist/
RPM_PACKAGE_SOURCE_DIR=$(RPM_PACKAGE_DIR)/SOURCES

PYTHONPATH=/home/marc/atix/comoonics-git/clustersuite/lib/

PACKAGES=comoonics-assistant-py comoonics-backup-legato-py comoonics-backup-py comoonics-base-py comoonics-cdsl-py comoonics-cluster-py \
	comoonics-cluster-tools-py comoonics-cmdb-py comoonics-db-py comoonics-dr-py comoonics-ec-admin-py comoonics-ec-base-py comoonics-ec-py \
	comoonics-imsd-plugins-py comoonics-imsd-py comoonics-installation-py comoonics-storage-hp-py comoonics-storage-py comoonics-tools-py
