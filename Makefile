include Makefile.inc
 
# comoonics-analysis-py
$(DISTDIR)/comoonics-analysis-py-$(VERSION).tar.gz: lib/comoonics/analysis/ComObjects.py \
			lib/comoonics/analysis/ComGLockParser.py lib/comoonics/analysis/ComGFSCountersWriters.py \
			lib/comoonics/analysis/__init__.py lib/comoonics/analysis/ComGLockWriters.py \
			lib/comoonics/analysis/ComWriters.py lib/comoonics/analysis/StraceAnalyser.py \
			lib/comoonics/analysis/ComParser.py
	bash ./build_rpm-analysis.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-assistant-py
$(DISTDIR)/comoonics-assistant-py-$(VERSION).tar.gz: lib/comoonics/assistant/ComClusterAssistantHelper.py \
		lib/comoonics/assistant/ComStorageAssistantHelper.py \
		lib/comoonics/assistant/ComConfigurationManagerTui.py \
		lib/comoonics/assistant/ComAssistantInfo.py \
		lib/comoonics/assistant/ComECAssistantController.py \
		lib/comoonics/assistant/ComAssistantHelper.py \
		lib/comoonics/assistant/__init__.py \
		lib/comoonics/assistant/ComAssistantController.py \
		lib/comoonics/assistant/ComAssistantTui.py \
		lib/comoonics/assistant/ComConfigurationManager.py
	bash ./build_rpm-assistant.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-backup-legato-py
$(DISTDIR)/comoonics-backup-legato-py-$(VERSION).tar.gz: lib/comoonics/backup/EMCLegato/ComEMCLegatoBackupHandler.py \
		lib/comoonics/backup/EMCLegato/ComEMCLegatoNetworker.py \
		lib/comoonics/backup/EMCLegato/__init__.py
	bash ./build_rpm-backup-legato.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-backup-py
$(DISTDIR)/comoonics-backup-py-$(VERSION).tar.gz: lib/comoonics/backup/__init__.py \
		lib/comoonics/backup/ComBackupHandler.py
	bash ./build_rpm-backup.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-base-py
$(DISTDIR)/comoonics-base-py-$(VERSION).tar.gz: lib/comoonics/ComPath.py \
			lib/comoonics/XmlTools.py lib/comoonics/ComGFS.py lib/comoonics/ComProperties.py lib/comoonics/ComExceptions.py \
			lib/comoonics/ComSysrq.py lib/comoonics/__init__.py lib/comoonics/DictTools.py lib/comoonics/ComLog.py \
			lib/comoonics/ComDataObject.py lib/comoonics/ComSystem.py
	bash ./build_rpm-base.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-cdsl-py
$(DISTDIR)/comoonics-cdsl-py-$(VERSION).tar.gz: lib/comoonics/cdsl/ComCdsl.py \
		lib/comoonics/cdsl/migration/MigrationTools.py \
		lib/comoonics/cdsl/migration/__init__.py \
		lib/comoonics/cdsl/ComCdslRepository.py \
		lib/comoonics/cdsl/__init__.py \
		lib/comoonics/cdsl/ComCdslValidate.py \
		bin/com-mkcdsl bin/com-cdslinvadm bin/com-cdslinvchk bin/com-rmcdsl
	@make -C man comoonics-cdsl-py
	bash ./build_rpm-cdsl.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-cluster-py
$(DISTDIR)/comoonics-cluster-py-$(VERSION).tar.gz: lib/comoonics/cluster/ComClusterInfo.py lib/comoonics/cluster/ComClusterNodeNic.py \
				lib/comoonics/cluster/ComClusterNode.py lib/comoonics/cluster/__init__.py \
				lib/comoonics/cluster/ComQueryMap.py \
				lib/comoonics/cluster/ComClusterRepository.py \
				bin/com-queryclusterconf
	@make -C man comoonics-cluster-py
	bash ./build_rpm-cluster.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-cluster-tools-py
$(DISTDIR)/comoonics-cluster-tools-py-$(VERSION).tar.gz: lib/comoonics/cluster/tools/__init__.py \
		lib/comoonics/cluster/tools/pxssh.py \
		lib/comoonics/cluster/tools/pexpect.py \
		bin/com-dsh bin/com-fence-validate bin/cl_checknodes
	bash ./build_rpm-cluster-tools.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-cmdb-py
$(DISTDIR)/comoonics-cmdb-py-$(VERSION).tar.gz: lib/comoonics/cmdb/ComSoftwareCMDB.py \
		lib/comoonics/cmdb/ComSource.py \
		lib/comoonics/cmdb/Packages.py \
		lib/comoonics/cmdb/__init__.py \
		lib/comoonics/cmdb/ComDSLStages.py \
		lib/comoonics/cmdb/ComDSL.py \
		lib/comoonics/cmdb/Reports.py \
		lib/comoonics/cmdb/Converter.py \
		lib/comoonics/cmdb/ComBaseDB.py \
		bin/com-rpmdiffs bin/com-rpm2db
	bash ./build_rpm-cmdb.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-db-py
$(DISTDIR)/comoonics-db-py-$(VERSION).tar.gz: lib/comoonics/db/ComDBLogger.py \
		lib/comoonics/db/ComDBConnection.py \
		lib/comoonics/db/__init__.py \
		lib/comoonics/db/ComDBJobs.py \
		lib/comoonics/db/ComDBObject.py \

	bash ./build_rpm-db.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-dr-py
$(DISTDIR)/comoonics-dr-py-$(VERSION).tar.gz: bin/comoonics-create-restoreimage  bin/comoonics-restore-system \
		xml/xml-dr/createlivecd.infodef.xml xml/xml-dr/drbackup.infodef.xml xml/xml-dr/drrestore.infodef.xml \
		xml/xml-dr/createlivecd.xml xml/xml-dr/drbackup.xml xml/xml-dr/drrestore.template.xml
	bash ./build_rpm-dr.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-ec-admin-py
$(DISTDIR)/comoonics-ec-admin-py-$(VERSION).tar.gz: xml/xml-ec-admin/localclone.disk2disk.infodef.xml \
		xml/xml-ec-admin/single-filesystem.backup.infodef.xml xml/xml-ec-admin/single-filesystem.restore.infodef.xml \
		xml/xml-ec-admin/localclone.disk2disk.template.xml  xml/xml-ec-admin/single-filesystem.backup.template.xml \
		xml/xml-ec-admin/single-filesystem.restore.template.xml
	bash ./build_rpm-ec-admin.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-ec-base-py
$(DISTDIR)/comoonics-ec-base-py-$(VERSION).tar.gz: lib/comoonics/ecbase/ComUtils.py \
		lib/comoonics/ecbase/__init__.py \
		lib/comoonics/ecbase/ComJournaled.py \
		lib/comoonics/ecbase/ComMetadataSerializer.py
	bash ./build_rpm-ec-base.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-ec-py
$(DISTDIR)/comoonics-ec-py-$(VERSION).tar.gz: 		lib/comoonics/enterprisecopy/ComStorageModificationset.py \
		lib/comoonics/enterprisecopy/ComRequirement.py \
		lib/comoonics/enterprisecopy/ComRegexpModification.py \
		lib/comoonics/enterprisecopy/ComCopyset.py \
		lib/comoonics/enterprisecopy/ComLVMCopyObject.py \
		lib/comoonics/enterprisecopy/ComPathCopyObject.py \
		lib/comoonics/enterprisecopy/ComPartitionCopyset.py \
		lib/comoonics/enterprisecopy/ComSCSIRequirement.py \
		lib/comoonics/enterprisecopy/ComPartitionModificationset.py \
		lib/comoonics/enterprisecopy/ComStorageCopyset.py \
		lib/comoonics/enterprisecopy/ComMessage.py \
		lib/comoonics/enterprisecopy/ComCatifModification.py \
		lib/comoonics/enterprisecopy/ComPathModificationset.py \
		lib/comoonics/enterprisecopy/ComMoveModification.py \
		lib/comoonics/enterprisecopy/__init__.py \
		lib/comoonics/enterprisecopy/ComCopyModification.py \
		lib/comoonics/enterprisecopy/ComModification.py \
		lib/comoonics/enterprisecopy/ComSysrqModification.py \
		lib/comoonics/enterprisecopy/ComStorageModification.py \
		lib/comoonics/enterprisecopy/ComCopyObject.py \
		lib/comoonics/enterprisecopy/ComPartitionCopyObject.py \
		lib/comoonics/enterprisecopy/ComFilesystemModificationset.py \
		lib/comoonics/enterprisecopy/ComModificationset.py \
		lib/comoonics/enterprisecopy/ComExecutionModification.py \
		lib/comoonics/enterprisecopy/ComEnterpriseCopy.py \
		lib/comoonics/enterprisecopy/ComFilesystemCopyset.py \
		lib/comoonics/enterprisecopy/ComArchiveRequirement.py \
		lib/comoonics/enterprisecopy/ComLVMCopyset.py \
		lib/comoonics/enterprisecopy/ComFilesystemCopyObject.py \
		lib/comoonics/enterprisecopy/ComBootloaderCopyset.py \
		lib/comoonics/enterprisecopy/ComFileModification.py \
		lib/comoonics/enterprisecopy/ComStorageCopyobject.py \
		lib/comoonics/enterprisecopy/ComISOFSModificationset.py \
		lib/comoonics/enterprisecopy/ComArchiveCopyObject.py \
		bin/com-ec
	bash ./build_rpm-ec.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-imsd-plugins-py
$(DISTDIR)/comoonics-imsd-plugins-py-$(VERSION).tar.gz: 		lib/comoonics/imsd/plugins/ComPlugin.py \
		lib/comoonics/imsd/plugins/ComSysrqPlugin.py \
		lib/comoonics/imsd/plugins/__init__.py \
		lib/comoonics/imsd/plugins/ComSysreportPlugin.py \
		lib/comoonics/imsd/plugins/ComSosReportPlugin.py
	bash ./build_rpm-imsd-plugins.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-imsd-py
$(DISTDIR)/comoonics-imsd-py-$(VERSION).tar.gz: lib/comoonics/imsd/__init__.py
	bash ./build_rpm-imsd.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-installation-py
$(DISTDIR)/comoonics-installation-py-$(VERSION).tar.gz: 		lib/comoonics/installation/osrcluster.py \
		lib/comoonics/installation/nfs.py \
		lib/comoonics/installation/__init__.py \
		lib/comoonics/installation/hosts.py
	bash ./build_rpm-installation.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-scsi-py
$(DISTDIR)/comoonics-scsi-py-$(VERSION).tar.gz: 		lib/comoonics/scsi/ComSCSIResolver.py \
		lib/comoonics/scsi/ComSCSI.py \
		lib/comoonics/scsi/__init__.py bin/com-rescanscsi
	bash ./build_rpm-scsi.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-search-py
$(DISTDIR)/comoonics-search-py-$(VERSION).tar.gz: 		lib/comoonics/search/__init__.py \
		lib/comoonics/search/SearchFormat.py
	bash ./build_rpm-search.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-storage-hp-py
$(DISTDIR)/comoonics-storage-hp-py-$(VERSION).tar.gz: lib/comoonics/storage/hp/ComHP_EVA_SSSU_Sim.py \
		lib/comoonics/storage/hp/ComHP_EVA_SSSU.py \
		lib/comoonics/storage/hp/ComHP_EVA_Storage.py \
		lib/comoonics/storage/hp/__init__.py \
		lib/comoonics/storage/hp/ComHP_EVA.py
	bash ./build_rpm-storage-hp.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-storage-py
$(DISTDIR)/comoonics-storage-py-$(VERSION).tar.gz: lib/comoonics/storage/ComPartition.py \
		lib/comoonics/storage/ComDevice.py \
		lib/comoonics/storage/ComLVM.py \
		lib/comoonics/storage/ComFile.py \
		lib/comoonics/storage/ComParted.py \
		lib/comoonics/storage/ComArchive.py \
		lib/comoonics/storage/ComBootDisk.py \
		lib/comoonics/storage/ComMountpoint.py \
		lib/comoonics/storage/ComScsi.py \
		lib/comoonics/storage/__init__.py \
		lib/comoonics/storage/ComFileSystem.py \
		lib/comoonics/storage/ComStorage.py \
		lib/comoonics/storage/ComDisk.py
	bash ./build_rpm-storage.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"

# comoonics-tools-py
$(DISTDIR)/comoonics-tools-py-$(VERSION).tar.gz: lib/comoonics/tools/poptparse.py \
		lib/comoonics/tools/ComSystemInformation.py \
		lib/comoonics/tools/ComSysreport.py \
		lib/comoonics/tools/__init__.py \
		lib/comoonics/tools/stabilized.py \
		lib/comoonics/tools/AutoDelegator.py \
		lib/comoonics/tools/odict.py \
		lib/comoonics/tools/lockfile.py \
		lib/comoonics/tools/XMLConfigParser.py \
		bin/stabilized
	bash ./build_rpm-tools.sh "$(COMOONICS_DISTRIBUTION)" "$(SHORTDISTRO)"
	
.PHONY: comoonics-analysis-py
comoonics-analysis-py: $(DISTDIR)/comoonics-analysis-py-$(VERSION).tar.gz
	
.PHONY: comoonics-assistant-py
comoonics-assistant-py: $(DISTDIR)/comoonics-assistant-py-$(VERSION).tar.gz
	
.PHONY: comoonics-backup-legato-py
comoonics-backup-legato-py: $(DISTDIR)/comoonics-backup-legato-py-$(VERSION).tar.gz
	
.PHONY: comoonics-backup-py
comoonics-backup-py: $(DISTDIR)/comoonics-backup-py-$(VERSION).tar.gz
	
.PHONY: comoonics-base-py
comoonics-base-py: $(DISTDIR)/comoonics-base-py-$(VERSION).tar.gz
	
.PHONY: comoonics-cdsl-py
comoonics-cdsl-py: $(DISTDIR)/comoonics-cdsl-py-$(VERSION).tar.gz
	
.PHONY: comoonics-cluster-py
comoonics-cluster-py: $(DISTDIR)/comoonics-cluster-py-$(VERSION).tar.gz
	
.PHONY: comoonics-cluster-tools-py
comoonics-cluster-tools-py: $(DISTDIR)/comoonics-cluster-tools-py-$(VERSION).tar.gz
	
.PHONY: comoonics-cmdb-py
comoonics-cmdb-py: $(DISTDIR)/comoonics-cmdb-py-$(VERSION).tar.gz
	
.PHONY: comoonics-db-py
comoonics-db-py: $(DISTDIR)/comoonics-db-py-$(VERSION).tar.gz
	
.PHONY: comoonics-dr-py
comoonics-dr-py: $(DISTDIR)/comoonics-dr-py-$(VERSION).tar.gz
	
.PHONY: comoonics-ec-admin-py
comoonics-ec-admin-py: $(DISTDIR)/comoonics-ec-admin-py-$(VERSION).tar.gz
	
.PHONY: comoonics-ec-base-py
comoonics-ec-base-py: $(DISTDIR)/comoonics-ec-base-py-$(VERSION).tar.gz
	
.PHONY: comoonics-ec-py
comoonics-ec-py: $(DISTDIR)/comoonics-ec-py-$(VERSION).tar.gz
	
.PHONY: comoonics-imsd-plugins-py
comoonics-imsd-plugins-py: $(DISTDIR)/comoonics-imsd-plugins-py-$(VERSION).tar.gz
	
.PHONY: comoonics-imsd-py
comoonics-imsd-py: $(DISTDIR)/comoonics-imsd-py-$(VERSION).tar.gz
	
.PHONY: comoonics-installation-py
comoonics-installation-py: $(DISTDIR)/comoonics-installation-py-$(VERSION).tar.gz
	
.PHONY: comoonics-scsi-py
comoonics-scsi-py: $(DISTDIR)/comoonics-scsi-py-$(VERSION).tar.gz

.PHONY: comoonics-search-py
comoonics-search-py: $(DISTDIR)/comoonics-search-py-$(VERSION).tar.gz
	
.PHONY: comoonics-storage-hp-py
comoonics-storage-hp-py: $(DISTDIR)/comoonics-storage-hp-py-$(VERSION).tar.gz
	
.PHONY: comoonics-storage-py
comoonics-storage-py: $(DISTDIR)/comoonics-storage-py-$(VERSION).tar.gz
	
.PHONY: comoonics-tools-py
comoonics-tools-py: $(DISTDIR)/comoonics-tools-py-$(VERSION).tar.gz

.PHONY: all
all: 
	make SHORTDISTRO=$(SHORTDISTRO) $(PACKAGES)

.PHONY: all-rhel5
all-rhel5: 
	make SHORTDISTRO=rhel5 $(PACKAGES)

.PHONY: all-rhel6
all-rhel6:
	make SHORTDISTRO=rhel6 $(PACKAGES)

.PHONY: all-sles11
all-sles11: 
	make SHORTDISTRO=sles11 $(PACKAGES)

.PHONY: test
test: 
	@if [ -z "$(NOTESTS)" ]; then \
		make -C lib test; \
	else \
		echo "Skipping tests."; \
	fi

.PHONY: binpackages
binpackages:
	PYTHONPATH=$(PYTHONPATH) NOTEST=1 SHORTDISTRO=$(SHORTDISTRO) ./build_all-specs.sh $(PACKAGES)	

.PHONY: bin
bin: test binpackages rpmsign

.PHONY: bin-rhel5
bin-rhel5:
	make SHORTDISTRO=rhel5 PACKAGES="$(PACKAGES)" bin	

.PHONY: bin-rhel6
bin-rhel6: 
	make SHORTDISTRO=rhel6 PACKAGES="$(PACKAGES)" bin	

.PHONY: bin-sles11
bin-sles11:
	make SHORTDISTRO=sles11 PACKAGES="$(PACKAGES)" bin	

.PHONY: man
man:
	@make -C man man

.PHONY: clean
clean:
	@make -C man clean
	for package in $(PACKAGES); do \
		rm -f $(DISTDIR)/$$package*; \
		rm -f $(RPM_PACKAGE_BIN_DIR)/$$package*; \
		rm -f $(RPM_PACKAGE_SRC_DIR)/$$package*; \
	done
	
.PHONY:rpmsign
rpmsign:
	@echo "Signing packages"
	rpm --resign $(RPM_PACKAGE_BIN_DIR)/$(PACKAGE_NAME)-*$(SHORTDISTRO)*.rpm $(RPM_PACKAGE_SRC_DIR)/$(PACKAGE_NAME)-*$(SHORTDISTRO).src.rpm

.PHONY: channel-rhel5
channel-rhel5:
	@make SHORTDISTRO=rhel5 channelcopy channelbuild

.PHONY: channel-rhel6
channel-rhel6:
	@make SHORTDISTRO=rhel6 channelcopy channelbuild

.PHONY: channel-sles11
channel-sles11:
	@make SHORTDISTRO=sles11 channelcopy channelbuild

.PHONY: channelcopy
channelcopy: 
	# Create an array of all CHANNELDIRS distros (second dir in path) and one without numbers at the end ready to be feeded in find
	for channel in $(CHANNELNAMES); do \
	    channelname=`echo $$channel | cut -f1 -d:`; \
	    channelalias=`echo $$channel | cut -f2 -d:`; \
       for architecture in $(ARCHITECTURES); do \
	      echo -n "Copying rpms to channel $(CHANNELDIR)/$$channelname/$(SHORTDISTRO)/$$architecture.."; \
	      ./install/copy_rpms.sh "$(SHORTDISTRO)" $(CHANNELDIR)/$$channelname $$channelalias $$architecture "$(PACKAGE_NAME)"; \
	      echo "(DONE)"; \
	   done; \
	done;
	
.PHONY: channelbuild
channelbuild:
	@echo "Rebuilding channels.."
	@for channel in $(CHANNELNAMES); do \
        channelname=`echo $$channel | cut -f1 -d:`; \
        $(CHANNELBASEDIR)/updaterepositories -s -r $(PRODUCTNAME)/$(PRODUCTVERSION)/$$channelname/$(SHORTDISTRO); \
	 done 
