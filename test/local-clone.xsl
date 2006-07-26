<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:output method="xml" doctype-system="/opt/atix/comoonics_cs/xml/comoonics-enterprise-copy.dtd" indent="yes"/>
  
  <xsl:template match="/">
    <xsl:variable name="clustername"><xsl:value-of select="localclone/cluster/@name"/></xsl:variable>
    <xsl:variable name="sbootdisk"><xsl:value-of select="localclone/sourcedisks/bootdisk/@name"/></xsl:variable>
    <xsl:variable name="dbootdisk"><xsl:value-of select="localclone/destdisks/bootdisk/@name"/></xsl:variable>
    <xsl:variable name="srootdisk"><xsl:value-of select="localclone/sourcedisks/rootdisk/@name"/></xsl:variable>
    <xsl:variable name="drootdisk"><xsl:value-of select="localclone/destdisks/rootdisk/@name"/></xsl:variable>
    <xsl:variable name="dbootpart"><xsl:value-of select="localclone/destpartitions/bootdisk/@name"/></xsl:variable>
    <xsl:variable name="drootpart"><xsl:value-of select="localclone/destpartitions/rootdisk/@name"/></xsl:variable>
    <xsl:variable name="kernelversion"><xsl:value-of select="localclone/kernel/@version"/></xsl:variable>
    <xsl:variable name="tmpdir"><xsl:value-of select="localclone/dirs/tmp/@name"/></xsl:variable>

<enterprisecopy name="{$clustername}-local-clone">
  <copyset name='copy-bootdisk' type='partition'>
    <source type='disk'>
      <disk name="{$sbootdisk}"/>
    </source>
    <destination type='disk'>
      <disk name="{$dbootdisk}"/>
    </destination>
  </copyset>
  <copyset name='copy-root' type='partition'>
    <source type='disk'>
      <disk name="{$srootdisk}"/>
    </source>
    <destination type='disk'>
      <disk name="{$drootdisk}"/>
    </destination>
  </copyset>
  <copyset name='copy-lvm-root' type='lvm'>
    <source type='lvm'>
      <volumegroup name="vg_{$clustername}_sr"/>
    </source>
    <destination type='lvm'>
      <volumegroup name="vg_{$clustername}_srC">
        <physicalvolume name="{$drootpart}"/>
      </volumegroup>
    </destination>
  </copyset>
  <copyset name='copy-sharedroot' type='filesystem'>
    <source type='filesystem'>
      <device name='/dev/vg_{$clustername}_sr/lv_sharedroot'>
        <filesystem type='gfs'/>
        <mountpoint name='/'/>
      </device>
    </source>
    <destination type='filesystem'>
      <device id='rootfs' name='/dev/vg_{$clustername}_srC/lv_sharedroot'>
        <filesystem clustername='{$clustername}' type='gfs'/>
        <mountpoint name='/mnt/dest'>
          <option value='lock_nolock' name='lockproto'/>
        </mountpoint>
      </device>
    </destination>
  </copyset>
  <copyset name='copy-boot' type='filesystem'>
    <source type='filesystem'>
      <device id='sourcebootfs' name='/dev/sda1'>
        <filesystem type='ext3'/>
        <mountpoint name='/mnt/source'/>
      </device>
    </source>
    <destination type='filesystem'>
      <device id='destbootfs' name='/dev/sdc1'>
        <filesystem type='ext3'/>
        <mountpoint name='/mnt/dest'/>
      </device>
    </destination>
  </copyset>
  <copyset type='bootloader'>
    <source type='none'/>
    <destination type='disk'>
      <disk name='/dev/sdc'/>
      <bootloader type='grub'/>
    </destination>
  </copyset>
  <modificationset name='modifyroot' type='filesystem'>
    <device refid='rootfs'>
      <modification search='&lt;rootvolume name=.*>' replace='&lt;rootvolume name="/dev/vg_{$clustername}_srC/lv_sharedroot">' type='regexp'>
        <file name='etc/cluster/cluster.conf'/>
      </modification>
    </device>
  </modificationset>
  <modificationset name='modifyboot' type='filesystem'>
    <device refid='destbootfs'>
      <modification search='vg_{$clustername}_sr/' replace='vg_{$clustername}_srB/' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='vg_{$clustername}_srC' replace='vg_{$clustername}_sr' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='vg_{$clustername}_srB' replace='vg_{$clustername}_srC' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='LocalClone' replace='B' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='SharedRoot \(' replace='SharedRoot LocalClone (' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='SharedRoot Failsave \(' replace='SharedRoot LocalClone Failsave (' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='SharedRoot B' replace='SharedRoot' type='regexp'>
        <file name='grub/grub.conf'/>
      </modification>
      <modification search='&lt;rootvolume name=".*">' replace='&lt;rootvolume name="/dev/vg_{$clustername}_srC/lv_sharedroot">' type='regexp'>
        <requirement dest='{$tmpdir}' name='/mnt/dest/initrd_sr-{$kernelversion}.img' format='cpio' type='archive'/>
        <file name='etc/cluster/cluster.conf'/>
      </modification>
    </device>
  </modificationset>
</enterprisecopy>
  </xsl:template>

</xsl:stylesheet>
