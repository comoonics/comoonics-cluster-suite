#!/usr/bin/python
"""distutils.command.bdist_rpm

Implements the Distutils 'bdist_rpm' command (create RPM source and binary
distributions)."""

# This module should be kept compatible with Python 2.1.

__revision__ = "$Id: setup.py,v 1.4 2009-09-29 16:13:37 marc Exp $"

from distutils.core import setup
import sys, os, string
import glob
from types import *
from distutils.core import Command
from distutils.debug import DEBUG
from distutils.util import get_platform
from distutils.file_util import write_file
from distutils.errors import *
from distutils.sysconfig import get_python_version, get_config_var
from distutils import log

class bdist_rpm_fedora (Command):

    description = "create an RPM distribution"
    slesinconsistentrpms={"PyXML": "pyxml"}

    user_options = [
        ('bdist-base=', None,
         "base directory for creating built distributions"),
        ('rpm-base=', None,
         "base directory for creating RPMs (defaults to \"rpm\" under "
         "--bdist-base; must be specified for RPM 2)"),
        ('dist-dir=', 'd',
         "directory to put final RPM files in "
         "(and .spec files if --spec-only)"),
        ('python=', None,
         "path to Python interpreter to hard-code in the .spec file "
         "(default: \"python\")"),
        ('fix-python', None,
         "hard-code the exact path to the current Python interpreter in "
         "the .spec file"),
        ('spec-only', None,
         "only regenerate spec file"),
        ('source-only', None,
         "only generate source RPM"),
        ('binary-only', None,
         "only generate binary RPM"),
        ('use-bzip2', None,
         "use bzip2 instead of gzip to create source distribution"),

        # More meta-data: too RPM-specific to put in the setup script,
        # but needs to go in the .spec file -- so we make these options
        # to "bdist_rpm".  The idea is that packagers would put this
        # info in setup.cfg, although they are of course free to
        # supply it on the command line.
        ('distribution-name=', None,
         "name of the (Linux) distribution to which this "
         "RPM applies (*not* the name of the module distribution!)"),
        ('group=', None,
         "package classification [default: \"Development/Libraries\"]"),
        ('release=', None,
         "RPM release number"),
        ('serial=', None,
         "RPM serial number"),
        ('vendor=', None,
         "RPM \"vendor\" (eg. \"Joe Blow <joe@example.com>\") "
         "[default: maintainer or author from setup script]"),
        ('packager=', None,
         "RPM packager (eg. \"Jane Doe <jane@example.net>\")"
         "[default: vendor]"),
        ('doc-files=', None,
         "list of documentation files (space or comma-separated)"),
        ('changelog=', None,
         "RPM changelog"),
        ('icon=', None,
         "name of icon file"),
        ('provides=', None,
         "capabilities provided by this package"),
        ('requires=', None,
         "capabilities required by this package"),
        ('conflicts=', None,
         "capabilities which conflict with this package"),
        ('build-requires=', None,
         "capabilities required to build this package"),
        ('obsoletes=', None,
         "capabilities made obsolete by this package"),
        ('no-autoreq', None,
         "do not automatically calculate dependencies"),

        # Actions to take when building RPM
        ('keep-temp', 'k',
         "don't clean up RPM build directory"),
        ('no-keep-temp', None,
         "clean up RPM build directory [default]"),
        ('use-rpm-opt-flags', None,
         "compile with RPM_OPT_FLAGS when building from source RPM"),
        ('no-rpm-opt-flags', None,
         "do not pass any RPM CFLAGS to compiler"),
        ('rpm3-mode', None,
         "RPM 3 compatibility mode (default)"),
        ('rpm2-mode', None,
         "RPM 2 compatibility mode"),

        # Add the hooks necessary for specifying custom scripts
        ('prep-script=', None,
         "Specify a script for the PREP phase of RPM building"),
        ('build-script=', None,
         "Specify a script for the BUILD phase of RPM building"),

        ('pre-install=', None,
         "Specify a script for the pre-INSTALL phase of RPM building"),
        ('install-script=', None,
         "Specify a script for the INSTALL phase of RPM building"),
        ('post-install=', None,
         "Specify a script for the post-INSTALL phase of RPM building"),

        ('pre-uninstall=', None,
         "Specify a script for the pre-UNINSTALL phase of RPM building"),
        ('post-uninstall=', None,
         "Specify a script for the post-UNINSTALL phase of RPM building"),

        ('clean-script=', None,
         "Specify a script for the CLEAN phase of RPM building"),

        ('verify-script=', None,
         "Specify a script for the VERIFY phase of the RPM build"),

        # Allow a packager to explicitly force an architecture
        ('force-arch=', None,
         "Force an architecture onto the RPM build process"),
       ]

    boolean_options = ['keep-temp', 'use-rpm-opt-flags', 'rpm3-mode',
                       'no-autoreq']

    negative_opt = {'no-keep-temp': 'keep-temp',
                    'no-rpm-opt-flags': 'use-rpm-opt-flags',
                    'rpm2-mode': 'rpm3-mode'}


    def initialize_options (self):
        self.bdist_base = None
        self.rpm_base = None
        self.dist_dir = None
        self.python = None
        self.fix_python = None
        self.spec_only = None
        self.binary_only = None
        self.source_only = None
        self.use_bzip2 = None

        self.distribution_name = None
        self.group = None
        self.release = None
        self.serial = None
        self.vendor = None
        self.packager = None
        self.doc_files = None
        self.changelog = None
        self.icon = None

        self.prep_script = None
        self.build_script = None
        self.install_script = None
        self.clean_script = None
        self.verify_script = None
        self.pre_install = None
        self.post_install = None
        self.pre_uninstall = None
        self.post_uninstall = None
        self.prep = None
        self.provides = None
        self.requires = None
        self.conflicts = None
        self.build_requires = None
        self.obsoletes = None

        self.keep_temp = 0
        self.use_rpm_opt_flags = 1
        self.rpm3_mode = 1
        self.no_autoreq = 0

        self.force_arch = None

    # initialize_options()


    def finalize_options (self):
        self.set_undefined_options('bdist', ('bdist_base', 'bdist_base'))
        if self.rpm_base is None:
            if not self.rpm3_mode:
                raise DistutilsOptionError, \
                      "you must specify --rpm-base in RPM 2 mode"
            self.rpm_base = os.path.join(self.bdist_base, "rpm")

        if self.python is None:
            if self.fix_python:
                self.python = sys.executable
            else:
                self.python = "python"
        elif self.fix_python:
            raise DistutilsOptionError, \
                  "--python and --fix-python are mutually exclusive options"

        if os.name != 'posix':
            raise DistutilsPlatformError, \
                  ("don't know how to create RPM "
                   "distributions on platform %s" % os.name)
        if self.binary_only and self.source_only:
            raise DistutilsOptionError, \
                  "cannot supply both '--source-only' and '--binary-only'"

        # don't pass CFLAGS to pure python distributions
        if not self.distribution.has_ext_modules():
            self.use_rpm_opt_flags = 0

        self.set_undefined_options('bdist', ('dist_dir', 'dist_dir'))
        self.finalize_package_data()

    # finalize_options()

    def finalize_package_data (self):
        self.ensure_string('group', "Development/Libraries")
        self.ensure_string('vendor',
                           "%s <%s>" % (self.distribution.get_contact(),
                                        self.distribution.get_contact_email()))
        self.ensure_string('packager')
        self.ensure_string_list('doc_files')
        if type(self.doc_files) is ListType:
            for readme in ('README', 'README.txt'):
                if os.path.exists(readme) and readme not in self.doc_files:
                    self.doc_files.append(readme)

        self.ensure_string('release', "1")
        self.ensure_string('serial')   # should it be an int?

        self.ensure_string('distribution_name')

        self.ensure_string('changelog')
          # Format changelog correctly
        self.changelog = self._format_changelog(self.changelog)

        self.ensure_filename('icon')

        self.ensure_filename('prep_script')
        self.ensure_filename('build_script')
        self.ensure_filename('install_script')
        self.ensure_filename('clean_script')
        self.ensure_filename('verify_script')
        self.ensure_filename('pre_install')
        self.ensure_filename('post_install')
        self.ensure_filename('pre_uninstall')
        self.ensure_filename('post_uninstall')

        # XXX don't forget we punted on summaries and descriptions -- they
        # should be handled here eventually!

        # Now *this* is some meta-data that belongs in the setup script...
        self.ensure_string_list('provides')
        self.ensure_string_list('requires')
        self.ensure_string_list('conflicts')
        self.ensure_string_list('build_requires')
        self.ensure_string_list('obsoletes')

        self.ensure_string('force_arch')
    # finalize_package_data ()


    def run (self):

        if DEBUG:
            print "before _get_package_data():"
            print "vendor =", self.vendor
            print "packager =", self.packager
            print "doc_files =", self.doc_files
            print "changelog =", self.changelog

        # make directories
        if self.spec_only:
            spec_dir = self.dist_dir
            self.mkpath(spec_dir)
        else:
            rpm_dir = {}
            for d in ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
                rpm_dir[d] = os.path.join(self.rpm_base, d)
                self.mkpath(rpm_dir[d])
            spec_dir = rpm_dir['SPECS']

        # Spec file goes into 'dist_dir' if '--spec-only specified',
        # build/rpm.<plat> otherwise.
        spec_path = os.path.join(spec_dir,
                                 "%s.spec" % self.distribution.get_name())
        self.execute(write_file,
                     (spec_path,
                      self._make_spec_file()),
                     "writing '%s'" % spec_path)

        if self.spec_only: # stop if requested
            return

        # Make a source distribution and copy to SOURCES directory with
        # optional icon.
        saved_dist_files = self.distribution.dist_files[:]
        sdist = self.reinitialize_command('sdist')
        if self.use_bzip2:
            sdist.formats = ['bztar']
        else:
            sdist.formats = ['gztar']
        self.run_command('sdist')
        self.distribution.dist_files = saved_dist_files

        source = sdist.get_archive_files()[0]
        source_dir = rpm_dir['SOURCES']
        self.copy_file(source, source_dir)

        if self.icon:
            if os.path.exists(self.icon):
                self.copy_file(self.icon, source_dir)
            else:
                raise DistutilsFileError, \
                      "icon file '%s' does not exist" % self.icon


        # build package
        log.info("building RPMs")
        rpm_cmd = ['rpm']
        if os.path.exists('/usr/bin/rpmbuild') or \
           os.path.exists('/bin/rpmbuild'):
            rpm_cmd = ['rpmbuild']
        if self.source_only: # what kind of RPMs?
            rpm_cmd.append('-bs')
        elif self.binary_only:
            rpm_cmd.append('-bb')
        else:
            rpm_cmd.append('-ba')
        if self.rpm3_mode:
            rpm_cmd.extend(['--define',
                             '_topdir %s' % os.path.abspath(self.rpm_base)])
        if not self.keep_temp:
            rpm_cmd.append('--clean')
        rpm_cmd.append(spec_path)
        # Determine the binary rpm names that should be built out of this spec
        # file
        # Note that some of these may not be really built (if the file
        # list is empty)
        nvr_string = "%{name}-%{version}-%{release}"
        src_rpm = nvr_string + ".src.rpm"
        non_src_rpm = "%{arch}/" + nvr_string + ".%{arch}.rpm"
        q_cmd = r"rpm -q --qf '%s %s\n' --specfile '%s'" % (
            src_rpm, non_src_rpm, spec_path)

        out = os.popen(q_cmd)
        binary_rpms = []
        source_rpm = None
        while 1:
            line = out.readline()
            if not line:
                break
            l = string.split(string.strip(line))
            assert(len(l) == 2)
            binary_rpms.append(l[1])
            # The source rpm is named after the first entry in the spec file
            if source_rpm is None:
                source_rpm = l[0]

        status = out.close()
        if status:
            raise DistutilsExecError("Failed to execute: %s" % repr(q_cmd))

        self.spawn(rpm_cmd)

        if not self.dry_run:
            if not self.binary_only:
                srpm = os.path.join(rpm_dir['SRPMS'], source_rpm)
                assert(os.path.exists(srpm))
                self.move_file(srpm, self.dist_dir)

            if not self.source_only:
                for rpm in binary_rpms:
                    rpm = os.path.join(rpm_dir['RPMS'], rpm)
                    if os.path.exists(rpm):
                        self.move_file(rpm, self.dist_dir)
    # run()

    def _dist_path(self, path):
        return os.path.join(self.dist_dir, os.path.basename(path))

    def _filterdistdepField(self, field, val):
        _filteredvalssles=list()
        _filteredvalselse=list()
        _vals=list()
        # quickhack to detect sles and rhel
        if type(val) is ListType:
            values=list()
            for value in val:
                if value in self.slesinconsistentrpms:
                    _filteredvalssles.append(self.slesinconsistentrpms[value])
                    _filteredvalselse.append(value)
                else:
                    _vals.append(value)
        elif val is not None:
            if val in self.slesinconsistentrpms:
                _filteredvalssles.append(self.slesinconsistentrpms[val])
                _filteredvalselse.append(val)
        else:
                _vals.append(val)
                
        return _filteredvalssles, _filteredvalselse, _vals

    def _make_spec_file(self):
        """Generate the text of an RPM spec file and return it as a
        list of strings (one per line).
        """
        # definitions and headers
        name=self.distribution.get_name()
        version=self.distribution.get_version().replace('-','_')
        release=self.release.replace('-','_')
        pythonversion26=int(sys.version[0])>2 or (int(sys.version[0])==2 and int(sys.version[2])>5)
        if pythonversion26:
            withegginfo="%{!?withegginfo: %define withegginfo 1}"
        else:
            withegginfo="%{!?withegginfo: %define withegginfo 0}"

        spec_file = [
            '%{!?sles: %global sles 0}',
            '%if %{sles}',
            '%{!?python_sitelib: %global python_sitelib %(%{__python} -c \'from distutils.sysconfig import get_python_lib; import sys; sys.lib="lib"; print get_python_lib(0)\')}',
            '%else',
            '%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}',
            '%endif',
            '%define modulename '+'comoonics',
            withegginfo,
            '',
            'Summary: ' + self.distribution.get_description(),
            ]

        # put locale summaries into spec file
        # XXX not supported for now (hard to put a dictionary
        # in a config file -- arg!)
        #for locale in self.summaries.keys():
        #    spec_file.append('Summary(%s): %s' % (locale,
        #                                          self.summaries[locale]))

        spec_file.extend([
            'Name: %s' %name,
            'Version: %s' %version,
            'Release: %s' %release,])

        # XXX yuck! this filename is available from the "sdist" command,
        # but only after it has run: and we create the spec file before
        # running "sdist", in case of --spec-only.
        if self.use_bzip2:
            spec_file.append('Source0: %s/%s-%%{version}.tar.bz2' %(self.distribution.get_url(), name))
        else:
            spec_file.append('Source0: %s/%s-%%{version}.tar.gz' %(self.distribution.get_url(), name))

        spec_file.extend([
            'License: ' + self.distribution.get_license(),
            'Group: ' + self.group,
            'BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)',])
#            'Prefix: %{_prefix}', ])

        if not self.force_arch:
            # noarch if no extension modules
            if not self.distribution.has_ext_modules():
                spec_file.append('BuildArch: noarch')
        else:
            spec_file.append( 'BuildArch: %s' % self.force_arch )

        # This is really ugly!
        for field in ('Packager',
                      'Provides',
                      'Requires',
                      'Conflicts',
                      'Obsoletes',
                      ):
            val = getattr(self, string.lower(field))
            
            filteredvalssles=None
            if string.lower(field) == "requires":
                filteredvalssles, filteredvalselse, val = self._filterdistdepField(string.lower(field), val)
            if type(val) is ListType:
                spec_file.append('%s: %s' % (field, string.join(val)))
            elif val is not None:
                spec_file.append('%s: %s' % (field, val))
                
            if filteredvalssles:
                spec_file.append("%if %{sles}")
                spec_file.append("Requires: %s" %string.join(filteredvalssles))
                spec_file.append("%else")
                spec_file.append("Requires: %s" %string.join(filteredvalselse))
                spec_file.append("%endif")


        if self.distribution.get_url() != 'UNKNOWN':
            spec_file.append('Url: ' + self.distribution.get_url())

        if self.distribution_name:
            spec_file.append('Distribution: ' + self.distribution_name)

        if self.build_requires:
            spec_file.append('BuildRequires: ' +
                             string.join(self.build_requires))

        if self.icon:
            spec_file.append('Icon: ' + os.path.basename(self.icon))

        if self.no_autoreq:
            spec_file.append('AutoReq: 0')

        spec_file.extend([
            '',
            '%description',
            self.distribution.get_long_description()
            ])

        # put locale descriptions into spec file
        # XXX again, suppressed because config file syntax doesn't
        # easily support this ;-(
        #for locale in self.descriptions.keys():
        #    spec_file.extend([
        #        '',
        #        '%description -l ' + locale,
        #        self.descriptions[locale],
        #        ])

        # rpm scripts
        # figure out default build script
        def_setup_call = "%s %s" % (self.python,os.path.basename(sys.argv[0]))
        def_build = "%s %%{name} build" %(def_setup_call)
        if self.use_rpm_opt_flags:
            def_build = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_build

        # insert contents of files

        # XXX this is kind of misleading: user-supplied options are files
        # that we open and interpolate into the spec file, but the defaults
        # are just text that we drop in as-is.  Hmmm.

        script_options = [
            ('prep', 'prep_script', "%setup -q"),
            ('build', 'build_script', def_build),
            ('install', 'install_script',
             ("rm -rf $RPM_BUILD_ROOT\n"
              "%s %%{name} install "
              "--root=$RPM_BUILD_ROOT --prefix=/usr "
              "--install-purelib=%%{python_sitelib}") %(def_setup_call)),
            ('clean', 'clean_script', "rm -rf $RPM_BUILD_ROOT"),
            ('verifyscript', 'verify_script', None),
            ('pre', 'pre_install', None),
            ('post', 'post_install', None),
            ('preun', 'pre_uninstall', None),
            ('postun', 'post_uninstall', None),
        ]

        for (rpm_opt, attr, default) in script_options:
            # Insert contents of file referred to, if no file is referred to
            # use 'default' as contents of script
            val = getattr(self, attr)
            if val or default:
                spec_file.extend([
                    '',
                    '%' + rpm_opt,])
                if val:
                    spec_file.extend(string.split(open(val, 'r').read(), '\n'))
                else:
                    spec_file.append(default)


        # files section
        modulepaths=self._build_modulepaths()
        spec_file.extend([
            '',
            '%files',
            '%defattr(-,root,root,-)',
            '%if %{withegginfo}',
            '%{python_sitelib}/*.egg-info',
            '%endif'
        ])
        print "modulepaths: %s" %modulepaths
        for modulepath in modulepaths:
            spec_file.extend([
                '%%dir %%{python_sitelib}/%s' %modulepath,
                '%%{python_sitelib}/%s/*.py' %modulepath,
                '%%{python_sitelib}/%s/*.pyc' %modulepath,
                '%%{python_sitelib}/%s/*.pyo' %modulepath,
            ])
        prefix=get_config_var("prefix")
        exec_prefix=get_config_var("exec_prefix")
        print "prefix: %s" %prefix
        print "exec_prefix: %s" %exec_prefix
        print "datafiles: %s" %self.distribution.data_files
        print "scripts: %s" %self.distribution.scripts

        if hasattr(self.distribution, "data_files") and getattr(self.distribution, "data_files") != None:
            for dir, files in self.distribution.data_files:
                for file in files:
                    if dir.startswith(os.sep.join(["share", "man"])):
                        # should be changed to check if this is a man
                        spec_file.append(os.path.join(prefix, dir, os.path.basename(file)))
                    else:
                        spec_file.append(os.path.join(os.path.join(prefix, dir), os.path.basename(file)))

        if hasattr(self.distribution, "scripts") and getattr(self.distribution, "scripts") != None:
            for bin in self.distribution.scripts:
                spec_file.append("%attr(0755, root, root) "+ os.path.join(prefix, "bin", os.path.basename(bin)))

        if self.doc_files:
            spec_file.append('%doc ' + string.join(self.doc_files))

        if self.changelog:
            spec_file.extend([
                '',
                '%changelog',])
            spec_file.extend(self.changelog)

        return spec_file

    # _make_spec_file ()

    def _build_modulepaths(self):
        import os
        pathnames=list()
        if hasattr(self.distribution, "py_modules") and getattr(self.distribution, "py_modules") != None:
            for module in self.distribution.py_modules:
                pathname=os.sep.join(module.split(".")[:-1])
                if not pathname in pathnames:
                    pathnames.append(pathname)
        if hasattr(self.distribution, "packages") and getattr(self.distribution, "packages") != None:
            for package in self.distribution.packages:
                pathnames.append(os.sep.join(package.split(".")))
        return pathnames

    def _format_changelog(self, changelog):
        """Format the changelog correctly and convert it to a list of strings
        """
        if not changelog:
            return changelog
        new_changelog = []
        for line in string.split(string.strip(changelog), '\n'):
            line = string.strip(line)
            if line[0] == '*':
                new_changelog.extend(['', line])
            elif line[0] == '-':
                new_changelog.append(line)
            else:
                new_changelog.append('  ' + line)

        # strip trailing newline inserted by first changelog entry
        if not new_changelog[0]:
            del new_changelog[0]

        return new_changelog

    # _format_changelog()

# Should become a command!
def buildmanpages(setupcfg):
    if setupcfg.has_key("data_files"):
        data_files=setupcfg["data_files"]
        for dir, files in data_files:
            if dir.startswith(os.sep.join(["share", "man"])):
                doc2man(setupcfg["name"], dir, files)

def doc2man(packagename, manpath, outmanpages):            
    import sys
    import re
    import os
    import gzip
    import commands

    cmd=None
    if os.path.exists("/usr/bin/db2x_docbook2man"):
        cmd="/usr/bin/db2x_docbook2man"
    elif os.path.exists("/usr/bin/docbook2x-man"):
        cmd="/usr/bin/docbook2x-man"
    else:
        print "ERROR: /usr/bin/db2x_docbook2man not installed !"
        print "  TIP: use \"yum install docbook2X\" to install the software"
        return

    manpages = "%s.xml" %packagename
    olddir=os.path.abspath(os.path.curdir)
    os.chdir("man/")
    if os.path.exists(manpages):
        commands.getstatusoutput("%s %s"%(cmd, manpages))
    else:
        os.chdir(olddir)
        return
    for manpage in outmanpages:
        inF = file("../"+manpage.replace(".gz","",1),"rb")
        s = inF.read()
        inF.close()

        outF = gzip.GzipFile("../"+manpage,"wb")
        outF.write(s)
        outF.close()

        os.remove("../"+manpage.replace(".gz","",1))

    os.chdir(olddir)

# class bdist_rpm
setup_cfg={ "comoonics-base-py": {
      "name":"comoonics-base-py",
      "version":"0.1",
      "description":"Comoonics minimum baselibraries",
      "long_description":""" 
Comoonics minimum baselibraries written in Python

Those are classes used by more other packages.
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.open-sharedroot.org/development/comoonics-base-py",
      "package_dir" :  { "": "lib/"},
      "py_modules" :   [ "comoonics.ComDataObject", 
                       "comoonics.ComExceptions",
                       "comoonics.DictTools",
                       "comoonics.ComProperties",
                       "comoonics.ComPath",
                       "comoonics.ComLog", 
                       "comoonics.ComSystem", 
                       "comoonics.XmlTools" ],
    },
    "comoonics-cluster-py": {
      "name": "comoonics-cluster-py",
      "version": "0.1",
      "description":"Comoonics cluster configuration utilities written in Python",
      "long_description": """ Comoonics cluster configuration utilities written in Python """,
#      author="ATIX AG - Marc Grimme",
#      author_email="grimme@atix.de",
      "url": "http://www.open-sharedroot.org/development/comoonics-cluster-py",
      "package_dir":  { "comoonics.cluster" : "lib/comoonics/cluster", "comoonics.cluster.helper": "lib/comoonics/cluster/helper"},
      "packages":     [ "comoonics.cluster", "comoonics.cluster.helper" ],
      "scripts":      [ "bin/com-queryclusterconf" ],
      "data_files":    [ ("share/man/man1",[ "man/com-queryclusterconf.1.gz" ]) ],
    },
    "comoonics-cdsl-py": { 
      "name": "comoonics-cdsl-py",
      "version": "0.2",
      "description": "Comoonics cdsl utilities and library written in Python",
      "long_description": """ Comoonics cdsl utilities and library written in Python """,
#      author="ATIX AG - Marc Grimme",
#      author_email="grimme@atix.de",
      "url": "http://www.open-sharedroot.org/development/comoonics-cdsl-py",
      "package_dir": { "comoonics.cdsl" : "lib/comoonics/cdsl"},
      "packages":      [ "comoonics.cdsl" ],
      "scripts":       [ "bin/com-mkcdsl", "bin/com-mkcdslinfrastructure", "bin/com-cdslinvchk", "bin/com-rmcdsl" ],
      "data_files":    [ ("share/man/man1",[ "man/com-mkcdslinfrastructure.1.gz", "man/com-mkcdsl.1.gz", "man/com-cdslinvchk.1.gz", "man/com-rmcdsl.1.gz" ]) ],
    },
    "comoonics-tools-py": {
      "name":"comoonics-tools-py",
      "version":"0.1",
      "description":"Comoonics base tools",
      "long_description":""" 
Comoonics basic tools written in Python

Those are classes used by more other packages.
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.open-sharedroot.org/development/comoonics-tools-py",
      "package_dir" :  { "": "lib/"},
      "py_modules" :   [ "comoonics.AutoDelegator", 
                       "comoonics.lockfile",
                       "comoonics.odict",
                       "comoonics.stabilized",
                       "comoonics.XMLConfigParser" ],
      "scripts":       [ "bin/stabilized" ],
    },
    "comoonics-cluster-tools-py": {
      "name":"comoonics-cluster-tools-py",
      "version":"0.1",
      "description":"Comoonics cluster tools",
      "long_description":""" 
Comoonics cluster tools written in Python

Those are tools to help using OSR clusters.
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.open-sharedroot.org/development/comoonics-cluster-tools-py",
      "package_dir" :  { "": "lib/"},
      "py_modules" :   [ "comoonics.pexpect", 
                       "comoonics.pxssh" ],
      "scripts":       [ "bin/com-dsh" ],
    },
    "comoonics-ec-base-py": {
      "name":"comoonics-ec-base-py",
      "version":"0.1",
      "description":"Comoonics Enterprise Copy base libraries",
      "long_description":""" 
Comoonics Enterprise Copy base libraries

Base libraries used for comoonics enterprise copy.
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.open-sharedroot.org/development/comoonics-ec-base-py",
      "package_dir" :  { "": "lib/"},
      "py_modules" :   [ "comoonics.ComJournaled", 
                       "comoonics.ComMetadataSerializer",
                       "comoonics.ComUtils" ],
    },
    "comoonics-dr-py": {
      "name":"comoonics-dr-py",
      "version":"0.1",
      "description":"Comoonics desaster recovery assistant written in Python",
      "long_description":""" 
Comoonics desaster recovery assistant written in Python
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.open-sharedroot.org/development/comoonics-dr-py",
      "package_dir" :  { "": "lib/"},
      "scripts":       [ "bin/comoonics-create-restoreimage", "bin/comoonics-restore-system" ],
      "data_files":    [ ("/etc/comoonics/enterprisecopy/xml-dr",[
             "xml/xml-dr/drbackup.xml",
             "xml/xml-dr/createlivecd.xml",
             "xml/xml-dr/drbackup.infodef.xml",
             "xml/xml-dr/createlivecd.infodef.xml",
             "xml/xml-dr/drrestore.template.xml",
             "xml/xml-dr/drrestore.infodef.xml"
            ]),]
    },
}

basedict=None
if setup_cfg.has_key(sys.argv[1]):
    basedict=setup_cfg[sys.argv[1]]
    sys.argv.remove(sys.argv[1])
elif setup_cfg.has_key(sys.argv[0]):
    basedict=setup_cfg[sys.argv[0]]
basedict["license"]="GPLv2+"
basedict["cmdclass"]={"bdist_rpm": bdist_rpm_fedora}
buildmanpages(basedict)
setup(**basedict)
