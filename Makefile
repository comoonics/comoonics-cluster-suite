include Makefile.inc
 
# comoonics-analysis-py
$(DISTDIR)/comoonics-analysis-py-$(VERSION).tar.gz: lib/comoonics/analysis/ComObjects.py \
			lib/comoonics/analysis/ComGLockParser.py lib/comoonics/analysis/ComGFSCountersWriters.py \
			lib/comoonics/analysis/__init__.py lib/comoonics/analysis/ComGLockWriters.py \
			lib/comoonics/analysis/ComWriters.py lib/comoonics/analysis/StraceAnalyser.py \
			lib/comoonics/analysis/ComParser.py
	./build_rpm-analysis.sh "$(COMOONICS_DISTRIBUTION)"

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
	./build_rpm-assistant.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-backup-legato-py
$(DISTDIR)/comoonics-backup-legato-py-$(VERSION).tar.gz: lib/comoonics/backup/EMCLegato/ComEMCLegatoBackupHandler.py \
		lib/comoonics/backup/EMCLegato/ComEMCLegatoNetworker.py \
		lib/comoonics/backup/EMCLegato/__init__.py
	./build_rpm-backup-legato.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-backup-py
$(DISTDIR)/comoonics-backup-py-$(VERSION).tar.gz: lib/comoonics/backup/__init__.py \
		lib/comoonics/backup/ComBackupHandler.py
	./build_rpm-backup.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-base-py
$(DISTDIR)/comoonics-base-py-$(VERSION).tar.gz: lib/comoonics/ComPath.py \
			lib/comoonics/XmlTools.py lib/comoonics/ComGFS.py lib/comoonics/ComProperties.py lib/comoonics/ComExceptions.py \
			lib/comoonics/ComSysrq.py lib/comoonics/__init__.py lib/comoonics/DictTools.py lib/comoonics/ComLog.py \
			lib/comoonics/ComDataObject.py lib/comoonics/ComSystem.py
	./build_rpm-base.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-cdsl-py
$(DISTDIR)/comoonics-cdsl-py-$(VERSION).tar.gz: lib/comoonics/cdsl/ComCdsl.py \
		lib/comoonics/cdsl/migration/MigrationTools.py \
		lib/comoonics/cdsl/migration/__init__.py \
		lib/comoonics/cdsl/ComCdslRepository.py \
		lib/comoonics/cdsl/__init__.py \
		lib/comoonics/cdsl/ComCdslValidate.py \
		bin/com-mkcdsl bin/com-cdslinvadm bin/com-cdslinvchk bin/com-rmcdsl
	./build_rpm-cdsl.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-cluster-py
$(DISTDIR)/comoonics-cluster-py-$(VERSION).tar.gz: lib/comoonics/cluster/ComClusterInfo.py lib/comoonics/cluster/ComClusterNodeNic.py \
				lib/comoonics/cluster/ComClusterNode.py lib/comoonics/cluster/__init__.py \
				lib/comoonics/cluster/ComQueryMap.py \
				lib/comoonics/cluster/ComClusterRepository.py \
				bin/com-queryclusterconf
	./build_rpm-cluster.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-cluster-tools-py
$(DISTDIR)/comoonics-cluster-tools-py-$(VERSION).tar.gz: lib/comoonics/cluster/tools/__init__.py \
		lib/comoonics/cluster/tools/pxssh.py \
		lib/comoonics/cluster/tools/pexpect.py \
		bin/com-dsh bin/com-fence-validate bin/cl_checknodes
	./build_rpm-cluster-tools.sh "$(COMOONICS_DISTRIBUTION)"

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
	./build_rpm-cmdb.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-db-py
$(DISTDIR)/comoonics-db-py-$(VERSION).tar.gz: lib/comoonics/db/ComDBLogger.py \
		lib/comoonics/db/ComDBConnection.py \
		lib/comoonics/db/__init__.py \
		lib/comoonics/db/ComDBJobs.py \
		lib/comoonics/db/ComDBObject.py \

	./build_rpm-db.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-dr-py
$(DISTDIR)/comoonics-dr-py-$(VERSION).tar.gz: bin/comoonics-create-restoreimage  bin/comoonics-restore-system \
		xml/xml-dr/createlivecd.infodef.xml xml/xml-dr/drbackup.infodef.xml xml/xml-dr/drrestore.infodef.xml \
		xml/xml-dr/createlivecd.xml xml/xml-dr/drbackup.xml xml/xml-dr/drrestore.template.xml
	./build_rpm-dr.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-ec-admin-py
$(DISTDIR)/comoonics-ec-admin-py-$(VERSION).tar.gz: xml/xml-ec-admin/localclone.disk2disk.infodef.xml \
		xml/xml-ec-admin/single-filesystem.backup.infodef.xml xml/xml-ec-admin/single-filesystem.restore.infodef.xml \
		xml/xml-ec-admin/localclone.disk2disk.template.xml  xml/xml-ec-admin/single-filesystem.backup.template.xml \
		xml/xml-ec-admin/single-filesystem.restore.template.xml
	./build_rpm-ec-admin.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-ec-base-py
$(DISTDIR)/comoonics-ec-base-py-$(VERSION).tar.gz: lib/comoonics/ecbase/ComUtils.py \
		lib/comoonics/ecbase/__init__.py \
		lib/comoonics/ecbase/ComJournaled.py \
		lib/comoonics/ecbase/ComMetadataSerializer.py
	./build_rpm-ec-base.sh "$(COMOONICS_DISTRIBUTION)"

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
	./build_rpm-ec.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-imsd-plugins-py
$(DISTDIR)/comoonics-imsd-plugins-py-$(VERSION).tar.gz: 		lib/comoonics/imsd/plugins/ComPlugin.py \
		lib/comoonics/imsd/plugins/ComSysrqPlugin.py \
		lib/comoonics/imsd/plugins/__init__.py \
		lib/comoonics/imsd/plugins/ComSysreportPlugin.py \
		lib/comoonics/imsd/plugins/ComSosReportPlugin.py
	./build_rpm-imsd-plugins.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-imsd-py
$(DISTDIR)/comoonics-imsd-py-$(VERSION).tar.gz: lib/comoonics/imsd/__init__.py
	./build_rpm-imsd.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-installation-py
$(DISTDIR)/comoonics-installation-py-$(VERSION).tar.gz: 		lib/comoonics/installation/osrcluster.py \
		lib/comoonics/installation/nfs.py \
		lib/comoonics/installation/__init__.py \
		lib/comoonics/installation/hosts.py
	./build_rpm-installation.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-scsi-py
$(DISTDIR)/comoonics-scsi-py-$(VERSION).tar.gz: 		lib/comoonics/scsi/ComSCSIResolver.py \
		lib/comoonics/scsi/ComSCSI.py \
		lib/comoonics/scsi/__init__.py bin/com-rescanscsi
	./build_rpm-scsi.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-search-py
$(DISTDIR)/comoonics-search-py-$(VERSION).tar.gz: 		lib/comoonics/search/__init__.py \
		lib/comoonics/search/SearchFormat.py
	./build_rpm-search.sh "$(COMOONICS_DISTRIBUTION)"

# comoonics-storage-hp-py
$(DISTDIR)/comoonics-storage-hp-py-$(VERSION).tar.gz: lib/comoonics/storage/hp/ComHP_EVA_SSSU_Sim.py \
		lib/comoonics/storage/hp/ComHP_EVA_SSSU.py \
		lib/comoonics/storage/hp/ComHP_EVA_Storage.py \
		lib/comoonics/storage/hp/__init__.py \
		lib/comoonics/storage/hp/ComHP_EVA.py
	./build_rpm-storage-hp.sh "$(COMOONICS_DISTRIBUTION)"

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
	./build_rpm-storage.sh "$(COMOONICS_DISTRIBUTION)"

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
	./build_rpm-tools.sh "$(COMOONICS_DISTRIBUTION)"

.PHONY: all
all: $(PACKAGES)

.PHONY: test
test: 
	@[ -z "$(NOTEST)"] && make -C lib test

.PHONY: bin
bin: test $(PACKAGES)
	PYTHONPATH=$(PYTHONPATH) NOTEST=1 ./build_all-specs.sh $?	

.PHONY: man
man:
	@make -C man man
	
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
	@make -C man $@
	
.PHONY: comoonics-cluster-py
comoonics-cluster-py: $(DISTDIR)/comoonics-cluster-py-$(VERSION).tar.gz
	@make -C man $@
	
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

.PHONY: clean
clean:
	@make -C man clean
	for package in $(PACKAGES); do \
		rm -f $(DISTDIR)/$$package*; \
	done