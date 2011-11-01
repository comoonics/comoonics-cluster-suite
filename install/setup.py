#!/usr/bin/python
"""distutils.command.bdist_rpm

Implements the Distutils 'bdist_rpm' command (create RPM source and binary
distributions)."""

# This module should be kept compatible with Python 2.1.

__revision__ = "$Id: setup.py,v 1.14 2011-02-15 14:57:37 marc Exp $"

oldglobals=globals()
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
import fnmatch
import unittest
import re

#=======================================================================================================================
# PydevTestRunner
#=======================================================================================================================
class PydevTestRunner:
    """ finds and runs a file or directory of files as a unit test """

    __py_extensions = ["*.py", "*.pyw"]
    __exclude_files = ["__init__.*"]

    def __init__(self, test_dir, test_filter=None, verbosity=2, tests=None, testfile_filter=None):
        self.test_dir = test_dir
        self.__adjust_path()
        self.test_filter = self.__setup_test_filter(test_filter)
        self.testfile_filter=testfile_filter
        if not self.testfile_filter:
            self.testfile_filter=list()
        self.verbosity = verbosity
        self.tests = tests


    def __adjust_path(self):
        """ add the current file or directory to the python path """
        path_to_append = None
        for n in xrange(len(self.test_dir)):
            dir_name = self.__unixify(self.test_dir[n])
            if os.path.isdir(dir_name):
                if not dir_name.endswith("/"):
                    self.test_dir[n] = dir_name + "/"
                path_to_append = os.path.normpath(dir_name)
            elif os.path.isfile(dir_name):
                path_to_append = os.path.dirname(dir_name)
            else:
                msg = ("unknown type. \n%s\nshould be file or a directory.\n" % (dir_name))
                raise RuntimeError(msg)
        if path_to_append is not None:
            #Add it as the last one (so, first things are resolved against the default dirs and 
            #if none resolves, then we try a relative import).
            sys.path.append(path_to_append)
        return

    def __setup_test_filter(self, test_filter):
        """ turn a filter string into a list of filter regexes """
        if test_filter is None or len(test_filter) == 0:
            return None
        return [re.compile("test%s" % f) for f in test_filter]

    def __is_valid_py_file(self, fname):
        """ tests that a particular file contains the proper file extension 
            and is not in the list of files to exclude """
        is_valid_fname = 0
        for invalid_fname in self.__class__.__exclude_files:
            is_valid_fname += int(not fnmatch.fnmatch(fname, invalid_fname))
        if_valid_ext = 0
        for ext in self.__class__.__py_extensions:
            if_valid_ext += int(fnmatch.fnmatch(fname, ext))
        return is_valid_fname > 0 and if_valid_ext > 0

    def __unixify(self, s):
        """ stupid windows. converts the backslash to forwardslash for consistency """
        return os.path.normpath(s).replace(os.sep, "/")

    def __importify(self, s, dir=False):
        """ turns directory separators into dots and removes the ".py*" extension 
            so the string can be used as import statement """
        if not dir:
            dirname, fname = os.path.split(s)

            if fname.count('.') > 1:
                #if there's a file named xxx.xx.py, it is not a valid module, so, let's not load it...
                return

            imp_stmt_pieces = [dirname.replace("\\", "/").replace("/", "."), os.path.splitext(fname)[0]]

            if len(imp_stmt_pieces[0]) == 0:
                imp_stmt_pieces = imp_stmt_pieces[1:]

            return ".".join(imp_stmt_pieces)

        else: #handle dir
            return s.replace("\\", "/").replace("/", ".")

    def __file_is_not_filtered(self, fname):
        return fname in self.testfile_filter

    def __add_files(self, pyfiles, root, files):
        """ if files match, appends them to pyfiles. used by os.path.walk fcn """
        for fname in files:
            if not self.__file_is_not_filtered(fname) and self.__is_valid_py_file(fname):
                name_without_base_dir = self.__unixify(os.path.join(root, fname))
                pyfiles.append(name_without_base_dir)
        return


    def find_import_files(self):
        """ return a list of files to import """
        pyfiles = []

        for base_dir in self.test_dir:
            if os.path.isdir(base_dir):
                if hasattr(os, 'walk'):
                    for root, dirs, files in os.walk(base_dir):
                        self.__add_files(pyfiles, root, files)
                else:
                    # jython2.1 is too old for os.walk!
                    os.path.walk(base_dir, self.__add_files, pyfiles)
            elif os.path.isfile(base_dir):
                pyfiles.append(base_dir)

        return pyfiles

    def __get_module_from_str(self, modname, print_exception):
        """ Import the module in the given import path.
            * Returns the "final" module, so importing "coilib40.subject.visu" 
            returns the "visu" module, not the "coilib40" as returned by __import__ """
        try:
            mod = __import__(modname)
            for part in modname.split('.')[1:]:
                mod = getattr(mod, part)
            return mod
        except:
            if print_exception:
                import traceback;traceback.print_exc()
                sys.stderr.write('ERROR: Module: %s could not be imported.\n' % (modname,))
            return None

    def find_modules_from_files(self, pyfiles):
        """ returns a lisst of modules given a list of files """
        #let's make sure that the paths we want are in the pythonpath...
        imports = [self.__importify(s) for s in pyfiles]

        system_paths = []
        for s in sys.path:
            system_paths.append(self.__importify(s, True))


        ret = []
        for imp in imports:
            if imp is None:
                continue #can happen if a file is not a valid module
            choices = []
            for s in system_paths:
                if imp.startswith(s):
                    add = imp[len(s) + 1:]
                    if add:
                        choices.append(add)
                    #sys.stdout.write(' ' + add + ' ')

            if not choices:
                sys.stdout.write('PYTHONPATH not found for file: %s\n' % imp)
            else:
                for i, import_str in enumerate(choices):
                    mod = self.__get_module_from_str(import_str, print_exception=i == len(choices) - 1)
                    if mod is not None:
                        ret.append(mod)
                        break


        return ret

    def find_tests_from_modules(self, modules):
        """ returns the unittests given a list of modules """
        loader = unittest.TestLoader()

        ret = []
        if self.tests:
            accepted_classes = {}
            accepted_methods = {}

            for t in self.tests:
                splitted = t.split('.')
                if len(splitted) == 1:
                    accepted_classes[t] = t

                elif len(splitted) == 2:
                    accepted_methods[t] = t

            #===========================================================================================================
            # GetTestCaseNames
            #===========================================================================================================
            class GetTestCaseNames:
                """Yes, we need a class for that (cannot use outer context on jython 2.1)"""

                def __init__(self, accepted_classes, accepted_methods):
                    self.accepted_classes = accepted_classes
                    self.accepted_methods = accepted_methods

                def __call__(self, testCaseClass):
                    """Return a sorted sequence of method names found within testCaseClass"""
                    testFnNames = []
                    className = testCaseClass.__name__

                    if DictContains(self.accepted_classes, className):
                        for attrname in dir(testCaseClass):
                            #If a class is chosen, we select all the 'test' methods'
                            if attrname.startswith('test') and hasattr(getattr(testCaseClass, attrname), '__call__'):
                                testFnNames.append(attrname)

                    else:
                        for attrname in dir(testCaseClass):
                            #If we have the class+method name, we must do a full check and have an exact match.
                            if DictContains(self.accepted_methods, className + '.' + attrname):
                                if hasattr(getattr(testCaseClass, attrname), '__call__'):
                                    testFnNames.append(attrname)

                    #sorted() is not available in jython 2.1
                    testFnNames.sort()
                    return testFnNames


            loader.getTestCaseNames = GetTestCaseNames(accepted_classes, accepted_methods)


        ret.extend([loader.loadTestsFromModule(m) for m in modules])

        return ret


    def filter_tests(self, test_objs):
        """ based on a filter name, only return those tests that have
            the test case names that match """
        test_suite = []
        for test_obj in test_objs:

            if isinstance(test_obj, unittest.TestSuite):
                if test_obj._tests:
                    test_obj._tests = self.filter_tests(test_obj._tests)
                    if test_obj._tests:
                        test_suite.append(test_obj)

            elif isinstance(test_obj, unittest.TestCase):
                test_cases = []
                for tc in test_objs:
                    try:
                        testMethodName = tc._TestCase__testMethodName
                    except AttributeError:
                        #changed in python 2.5
                        testMethodName = tc._testMethodName

                    if self.__match(self.test_filter, testMethodName) and self.__match_tests(self.tests, tc, testMethodName):
                        test_cases.append(tc)
                return test_cases
        return test_suite


    def __match_tests(self, tests, test_case, test_method_name):
        if not tests:
            return 1

        for t in tests:
            class_and_method = t.split('.')
            if len(class_and_method) == 1:
                #only class name
                if class_and_method[0] == test_case.__class__.__name__:
                    return 1

            elif len(class_and_method) == 2:
                if class_and_method[0] == test_case.__class__.__name__ and class_and_method[1] == test_method_name:
                    return 1

        return 0




    def __match(self, filter_list, name):
        """ returns whether a test name matches the test filter """
        if filter_list is None:
            return 1
        for f in filter_list:
            if re.match(f, name):
                return 1
        return 0


    def run_tests(self):
        """ runs all tests """
        import sys
        sys.stdout.write("Finding files...\n")
        files = self.find_import_files()
        sys.stdout.write('%s %s\n' % (self.test_dir, '... done'))
        sys.stdout.write("Importing test modules %s ... " %files)
        modules = self.find_modules_from_files(files)
        sys.stdout.write("done.\n")
        sys.stdout.write("Testfilter: %s\n" %self.test_filter)
        sys.stdout.write("Curdir: %s\n" %os.path.realpath(os.path.curdir))
        sys.stdout.write("Pythonpath: %s\n" %sys.path)
        all_tests = self.find_tests_from_modules(modules)
        if self.test_filter or self.tests:

            if self.test_filter:
                sys.stdout.write('Test Filter: %s' % ([p.pattern for p in self.test_filter],))

            if self.tests:
                sys.stdout.write('Tests to run: %s' % (self.tests,))

            all_tests = self.filter_tests(all_tests)

        sys.stdout.write('\n')
        runner = unittest.TextTestRunner(stream=sys.stdout, descriptions=1, verbosity=self.verbosity)
        return runner.run(unittest.TestSuite(all_tests))

class bdist_rpm_fedora (Command):

    description = "create an RPM distribution"
    slesinconsistentrpms={"PyXML": "pyxml", "python-devel": None }

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
        ('defines=', None, "Specify a list of defines.")
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
        self.defines = None

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
        self.ensure_string_list("defines")

        self.ensure_string('force_arch')
    # finalize_package_data ()


    def run (self):

        if DEBUG:
            print "before _get_package_data():"
            print "vendor =", self.vendor
            print "packager =", self.packager
            print "doc_files =", self.doc_files
            print "changelog =", self.changelog
            print "defines =", self.defines

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
        if self.defines:
            for define in self.defines:
                rpm_cmd.extend(['--define', define.replace("=", " ")])
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
        defines=""
        for define in self.defines:
            defines='--define "'+define.replace("=", " ")+'" '+defines
        q_cmd = r"rpm %s -q --qf '%s %s\n' --specfile '%s'" % (
            defines, src_rpm, non_src_rpm, spec_path)

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
                    if self.slesinconsistentrpms[value] != None:
                        _filteredvalssles.append(self.slesinconsistentrpms[value])
                    _filteredvalselse.append(value)
                else:
                    _vals.append(value)
        elif val is not None:
            if val in self.slesinconsistentrpms:
                if self.slesinconsistentrpms[val] != None:
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

        # also test by default
        withtest="%{!?withtest: %define withtest 1}"
        
        spec_file = [
            '%{!?sles: %global sles 0}',
            '%if %{sles}',
            '%{!?python_sitelib: %global python_sitelib %(%{__python} -c \'from distutils.sysconfig import get_python_lib; import sys; sys.lib="lib"; print get_python_lib(0)\')}',
            '%else',
            '%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}',
            '%endif',
            '%define modulename '+'comoonics',
            '%{!?LINUXDISTROSHORT: %global LINUXDISTROSHORT rhel5}',
            withegginfo,
            withtest,
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
            if (string.lower(field) == "requires" or string.lower(field) == "build_requires") and val != None:
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
            filteredvalssles=list()
            filteredvalselse=list()
            for val in self.build_requires:
                list1, list2, val = self._filterdistdepField("", val)
                filteredvalssles.extend(list1)
                filteredvalselse.extend(list2)
            
            if len(filteredvalselse) > 0:
                filteredvalssles.extend(val)
                filteredvalselse.extend(val)
                spec_file.append("%if %{sles}")
                if len(filteredvalssles) > 0:
                    spec_file.append("BuildRequires: %s" %string.join(filteredvalssles))
                spec_file.append("%else")
                spec_file.append("BuildRequires: %s" %string.join(filteredvalselse))
                spec_file.append("%endif")
            else:
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
        def_test1 = "%s %%{name} test" %(def_setup_call)
        if self.use_rpm_opt_flags:
            def_test1 = 'env CFLAGS="$RPM_OPT_FLAGS" ' + def_test1
        def_test="""%%if %%{withtest}
%s
%%endif
""" %def_test1

        # insert contents of files

        # XXX this is kind of misleading: user-supplied options are files
        # that we open and interpolate into the spec file, but the defaults
        # are just text that we drop in as-is.  Hmmm.

        script_options = [
            ('prep', 'prep_script', "%setup -q"),
            ('build', 'build_script', def_build+"\n"+def_test),
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

class test (Command):

    description = "tests everything needed to be installed"

    user_options = [
        ('build-base=', 'b',
         "base directory for build library"),
        ('test-base=', 't',
         "test directory for test library"),
        ('testfile-filter=', 'f',
         'which testfiles should be filtered'),
        ('testclass-filter=', 'c',
         'which testfiles classe should be filtered.'),
        ('testfile-exec=', 't',
         'execute the files being listed here instead of interpreting those')
        ]

    boolean_options = []

    help_options = [
        ]

    def initialize_options (self):
        import os.path
        self.build_base = os.path.join('build', 'lib')
        self.test_base="test"
        self.debug = None
        self.testclass_filter=list()
        self.testfile_filter=list()
        self.testfile_exec=list()

    def finalize_options (self):
        if self.testclass_filter and isinstance(self.testclass_filter, basestring):
            self.testclass_filter=[ self.testclass_filter ]
        if self.testfile_filter and isinstance(self.testfile_filter, basestring):
            self.testfile_filter=[ self.testfile_filter ]
        if self.testfile_exec and isinstance(self.testfile_exec, basestring):
            self.testfile_exec=self._resolve_glob(self.testfile_exec)
            self.testfile_filter.extend(self.testfile_exec)

    def _resolve_glob(self, searchstring):
        import glob
        return glob.glob(searchstring)

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

    def _get_testdir(self):
        import glob
        import os.path
        testdirs=list()
        for modulepath in self._build_modulepaths():
            path=os.path.join("lib", modulepath, self.test_base)
            print "Path: %s" %path
            if os.path.isdir(path):
                testdirs.append(path)
        return testdirs

    def newglobals(self, filetoexec):
        #patch provided by: Scott Schlesier - when script is run, it does not 
        #use globals from pydevd:
        #This will prevent the pydevd script from contaminating the namespace for the script to be debugged
        
        #pretend pydevd is not the main module, and
        #convince the file to be debugged that it was loaded as main
        #sys.modules['setup'] = sys.modules['__main__']
        #sys.modules['setup'].__name__ = 'setup'            
        
        from imp import new_module
        m = new_module('__main__')
        #sys.modules['__main__'] = m
        m.__file__ = filetoexec
        myglobals = m.__dict__
        return m, myglobals

    def execfile(self, filetoexec, oglobals=None, mylocals=None):
#        oldglobals=dict()
#        for key in globals().keys():
#            oldglobals[key]=globals()[key]
        if oglobals is None:
            m, oglobals=self.newglobals(filetoexec)
        if mylocals is None: 
            mylocals = oglobals        
            
        #Predefined (writable) attributes: __name__ is the module's name; 
        #__doc__ is the module's documentation string, or None if unavailable; 
        #__file__ is the pathname of the file from which the module was loaded, 
        #if it was loaded from a file. The __file__ attribute is not present for 
        #C modules that are statically linked into the interpreter; for extension modules 
        #loaded dynamically from a shared library, it is the pathname of the shared library file. 


        #I think this is an ugly hack, bug it works (seems to) for the bug that says that sys.path should be the same in
        #debug and run.
        msys=__import__("sys", oglobals, mylocals)
        oglobals["sys"]=msys
        if m.__file__.startswith(oglobals["sys"].path[0]):
            #print >> sys.stderr, 'Deleting: ', sys.path[0]
            del oglobals["sys"].path[0]
        
        #now, the local directory has to be added to the pythonpath
        #sys.path.insert(0, os.getcwd())
        #Changed: it's not the local directory, but the directory of the file launched
        #The file being run ust be in the pythonpath (even if it was not before)
        oglobals["sys"].path.insert(0, os.path.split(filetoexec)[0])
        
        oldargv=sys.argv
        oglobals["sys"].argv=[ filetoexec, ]
        # for completness, we'll register the pydevd.reader & pydevd.writer threads
        try:
            execfile(filetoexec, oglobals, mylocals) #execute the script
#            sys.modules['__main__']=sys.modules['setup']
#            sys.modules['__main__'].__name__ = '__main__'
        except SystemExit, se:
            if se and se.code!=0 and se.code!=True:
                raise se
 #       for key in oldglobals.keys():
 #           globals()[key]=oldglobals[key]
            
        for key in globals().keys():
            if not key in oldglobals.keys():
                del globals()[key]
        sys.argv=oldargv
    
    def run (self):
        print "test:Hello world!"
        print "I'm: %s"%self.distribution
        print "build_base: %s" %self.build_base
        print "test_base: %s" %self.test_base
        print "Modulepath: %s" %self._build_modulepaths()
        print "Testdir: %s" %self._get_testdir()
        print "Testexecfiles: %s" %self.testfile_exec
        print "Testfilefilter: %s" %self.testfile_filter
        print "Testclassfilter: %s" %self.testclass_filter
        testdirs=self._get_testdir()
        mypath=list()
        mypath.append(os.path.join(os.getcwd(),self.build_base))
        if testdirs and len(testdirs)>0:
            mypath.extend(testdirs)
        mypath.extend(sys.path)
        sys.path=mypath
        print "Paths: %s" %sys.path
#        if self.testfile_exec and len(self.testfile_exec)>0:
#            for testfile_exec in self.testfile_exec:
#                print "Executing testfile %s" %testfile_exec
#                self.execfile(testfile_exec)
        if testdirs and len(testdirs)>0:
            result=PydevTestRunner(testdirs, self.testclass_filter, 3, None, self.testfile_filter).run_tests()
            if len(result.errors) + len(result.failures):
                raise IOError("Error test failed: %s" %result)

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
setup_cfg={ "comoonics-analysis-py": {
      "name":"comoonics-analysis-py",
      "version": "5.0",
      "description":"com.oonics analysis library written in Python",
      "long_description":""" 
com.oonics analysis library written in Python
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-analysis-py",
      "package_dir" :  { "comoonics.assistant": "lib/comoonics/analysis"},
      "packages": [ "comoonics.analysis" ],
      "scripts":       [ "bin/strace_analyser" ],
    },
    "comoonics-assistant-py": {
      "name":"comoonics-assistant-py",
      "version": "5.0",
      "description":"com.oonics assistant library written in Python",
      "long_description":""" 
com.oonics assistant library written in Python
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-assistant-py",
      "package_dir" :  { "comoonics.assistant": "lib/comoonics/assistant"},
      "packages": [ "comoonics.assistant" ],
    },
    "comoonics-backup-legato-py": {
      "name":"comoonics-backup-legato-py",
      "version": "5.0",
      "description":"com.oonics Legato Backup utilities and libraries written in Python",
      "long_description":""" 
com.oonics Legato Backup utilities and libraries written in Python
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-backup-legato-py",
      "package_dir" :  { "comoonics.backup.EMCLegato": "lib/comoonics/backup/EMCLegato"},
      "packages": [ "comoonics.backup.EMCLegato" ],
    },    
    "comoonics-backup-py": {
      "name":"comoonics-backup-py",
      "version": "5.0",
      "description":"com.oonics Backup utilities and libraries written in Python",
      "long_description":""" 
com.oonics Backup utilities and libraries written in Python
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-backup-py",
      "package_dir" :  { "comoonics.backup": "lib/comoonics/backup"},
      "packages": [ "comoonics.backup" ],
    },    
    "comoonics-base-py": {
      "name":"comoonics-base-py",
      "version": "5.0",
      "description":"com.oonics minimum baselibraries",
      "long_description":""" 
com.oonics minimum baselibraries written in Python

Those are classes used by more other packages.
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-base-py",
      "package_dir" :  { "": "lib/"},
      "packages": [ "comoonics" ],
#      "py_modules" :   [ "comoonics.ComDataObject", 
#                       "comoonics.ComExceptions",
#                       "comoonics.DictTools",
#                       "comoonics.ComProperties",
#                       "comoonics.ComPath",
#                       "comoonics.ComLog", 
#                       "comoonics.ComSystem", 
#                       "comoonics.XmlTools" ],
    },
    "comoonics-cdsl-py": { 
      "name": "comoonics-cdsl-py",
      "version": "5.0",
      "description": "com.oonics cdsl utilities and library written in Python",
      "long_description": """ com.oonics cdsl utilities and library written in Python """,
#      author="ATIX AG - Marc Grimme",
#      author_email="grimme@atix.de",
      "url": "http://www.comoonics.org/development/comoonics-cdsl-py",
      "package_dir": { "comoonics.cdsl" : "lib/comoonics/cdsl", "comoonics.cdsl.migration": "lib/comoonics/cdsl/migration" },
      "packages":      [ "comoonics.cdsl", "comoonics.cdsl.migration" ],
      "scripts":       [ "bin/com-mkcdsl", "bin/com-cdslinvadm", "bin/com-cdslinvchk", "bin/com-rmcdsl" ],
      "data_files":    [ ("share/man/man1",[ "man/com-cdslinvadm.1.gz", "man/com-mkcdsl.1.gz", "man/com-cdslinvchk.1.gz", "man/com-rmcdsl.1.gz" ]) ],
    },
    "comoonics-cluster-tools-py": {
      "name":"comoonics-cluster-tools-py",
      "version": "5.0",
      "description":"com.oonics cluster tools",
      "long_description":""" 
com.oonics cluster tools written in Python

Those are tools to help using OSR clusters.
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-cluster-tools-py",
      "package_dir" :  { "": "lib/"},
      "packages":      [ "comoonics.cluster.tools" ],
      "scripts":       [ "bin/com-dsh", "bin/cl_checknodes", "bin/com-fence-validate" ],
    },
    "comoonics-cluster-py": {
      "name": "comoonics-cluster-py",
      "version": "5.0",
      "description":"com.oonics cluster configuration utilities written in Python",
      "long_description": """ com.oonics cluster configuration utilities written in Python """,
#      author="ATIX AG - Marc Grimme",
#      author_email="grimme@atix.de",
      "url": "http://www.comoonics.org/development/comoonics-cluster-py",
      "package_dir":  { "comoonics.cluster" : "lib/comoonics/cluster", "comoonics.cluster.helper": "lib/comoonics/cluster/helper"},
      "packages":     [ "comoonics.cluster", "comoonics.cluster.helper" ],
      "scripts":      [ "bin/com-queryclusterconf" ],
      "data_files":    [ ("share/man/man1",[ "man/com-queryclusterconf.1.gz" ]) ],
    },
    "comoonics-cmdb-py": {
      "name":"comoonics-cmdb-py",
      "version": "5.0",
      "description":"com.oonics Softwaremanagement CMDB utilities and libraries written in Python",
      "long_description":""" 
com.oonics Softwaremanagement CMDB utilities and libraries written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-cmdb-py",
      "package_dir" :  { "comoonics.cmdb": "lib/comoonics/cmdb"},
      "packages": [ "comoonics.cmdb" ],
      "scripts":       [ "bin/com-channel2db", "bin/com-rpm2db", "bin/com-rpmdiffs", "bin/com-sysinfo" ],
    },    
    "comoonics-db-py": {
      "name":"comoonics-db-py",
      "version": "5.0",
      "description":"com.oonics Softwaremanagement Database utilities and libraries written in Python",
      "long_description":""" 
com.oonics Softwaremanagement Database utilities and libraries written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-db-py",
      "package_dir" :  { "comoonics.db": "lib/comoonics/db"},
      "packages": [ "comoonics.db" ],
    },    
    "comoonics-dr-py": {
      "name":"comoonics-dr-py",
      "version": "5.0",
      "description":"com.oonics desaster recovery assistant written in Python",
      "long_description":""" 
com.oonics desaster recovery assistant written in Python
""",
#      "author":"ATIX AG - Mark Hlawatschek",
#      "author_email":"hlawatschek@atix.de",
      "url":"http://www.comoonics.org/development/comoonics-dr-py",
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
    "comoonics-ec-admin-py": {
      "name":"comoonics-ec-admin-py",
      "version": "5.0",
      "description":"com.oonics enterprise copy administrator written in Python",
      "long_description":""" 
com.oonics enterprise copy administrator written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-ec-admin-py",
      "data_files":    [ ("/etc/comoonics/enterprisecopy/xml-ec-admin",[
            "xml/xml-ec-admin/localclone.disk2disk.infodef.xml",
            "xml/xml-ec-admin/localclone.disk2disk.template.xml",
            "xml/xml-ec-admin/single-filesystem.backup.infodef.xml",
            "xml/xml-ec-admin/single-filesystem.backup.template.xml",
            "xml/xml-ec-admin/single-filesystem.restore.infodef.xml",
            "xml/xml-ec-admin/single-filesystem.restore.template.xml"
            ]),]
    },    
    "comoonics-ec-base-py": {
      "name":"comoonics-ec-base-py",
      "version": "5.0",
      "description":"com.oonics Enterprise Copy base libraries",
      "long_description":""" 
com.oonics Enterprise Copy base libraries

Base libraries used for comoonics enterprise copy.
""",
      "url":"http://www.comoonics.org/development/comoonics-ec-base-py",
      "package_dir" :  { "": "lib/"},
      "packages": [ "comoonics.ecbase" ],
#      "py_modules" :   [ "comoonics.ecbase.ComJournaled", 
#                       "comoonics.ecbase.ComMetadataSerializer",
#                       "comoonics.ecbase.ComUtils" ],
    },
    "comoonics-ec-py": {
      "name":"comoonics-ec-py",
      "version": "5.0",
      "description":"com.oonics Enterprisecopy utilities and libraries written in Python",
      "long_description":""" 
com.oonics Enterprisecopy utilities and libraries written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-ec-py",
      "package_dir" :  { "comoonics.enterprisecopy": "lib/comoonics/enterprisecopy"},
      "packages": [ "comoonics.enterprisecopy" ],
      "scripts": [ "bin/com-ec" ]
    },    
    "comoonics-imsd-plugins-py": {
      "name":"comoonics-imsd-plugins-py",
      "version": "5.0",
      "description":"com.oonics imsd plugins written in Python",
      "long_description":""" 
com.oonics imsd plugins written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-imsd-plugins-py",
      "package_dir" :  { "comoonics.imsd.plugins": "lib/comoonics/imsd/plugins"},
      "packages": [ "comoonics.imsd.plugins" ],
    },    
    "comoonics-imsd-py": {
      "name":"comoonics-imsd-py",
      "version": "5.0",
      "description":"com.oonics imsd utilities and libraries written in Python",
      "long_description":""" 
com.oonics imsd utilities and libraries written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-imsd-py",
      "package_dir" :  { "comoonics.imsd": "lib/comoonics/imsd"},
      "packages": [ "comoonics.imsd" ],
    },    
    "comoonics-installation-py": {
      "name":"comoonics-installation-py",
      "version": "5.0",
      "description":"com.oonics installation library written in Python",
      "long_description":""" 
com.oonics installation library written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-installation-py",
      "package_dir" :  { "comoonics.installation": "lib/comoonics/installation"},
      "packages": [ "comoonics.installation" ],
    },    
    "comoonics-scsi-py": {
      "name":"comoonics-scsi-py",
      "version": "5.0",
      "description":"com.oonics SCSI utilities and libraries written in Python",
      "long_description":""" 
com.oonics SCSI utilities and libraries written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-scsi-py",
      "package_dir" :  { "comoonics.scsi": "lib/comoonics/scsi"},
      "packages": [ "comoonics.scsi" ],
      "scripts": [ "bin/com-rescanscsi" ]
    },    
    "comoonics-search-py": {
      "name":"comoonics-search-py",
      "version": "5.0",
      "description": "Searchlibraries used by mgrep",
      "long_description":""" 
Searchlibraries used by mgrep
""",
      "url":"http://www.comoonics.org/development/comoonics-search-py",
      "package_dir" :  { "comoonics.search": "lib/comoonics/search",
                         "comoonics.search.datetime": "lib/comoonics/search/datetime" },
      "packages": [ "comoonics.search", "comoonics.search.datetime" ],
    },    
    "comoonics-storage-hp-py": {
      "name":"comoonics-storage-hp-py",
      "version": "5.0",
      "description":"com.oonics Enterprisecopy HP Storage utilities and libraries written in Python",
      "long_description":""" 
com.oonics Enterprisecopy HP Storage utilities and libraries written in Python
""",
      "url":"http://www.comoonics.org/development/comoonics-storage-hp-py",
      "package_dir" :  { "comoonics.storage.hp": "lib/comoonics/storage/hp"},
      "packages": [ "comoonics.storage.hp" ],
    },    
    "comoonics-storage-py": {
      "name":"comoonics-storage-py",
      "version": "5.0",
      "description":"com.oonics Enterprisecopy Storage utilities and libraries written in Python",
      "long_description":""" 
com.oonics Enterprisecopy Storage utilities and libraries written in Python
""",
      "url": "http://www.comoonics.org/development/comoonics-storage-py",
      "package_dir" :  { "comoonics.storage": "lib/comoonics/storage"},
      "packages": [ "comoonics.storage" ],
    },    
    "comoonics-tools-py": {
      "name":"comoonics-tools-py",
      "version": "5.0",
      "description":"com.oonics base tools",
      "long_description":""" 
com.oonics basic tools written in Python

Those are classes used by more other packages.
""",
      "url":"http://www.comoonics.org/development/comoonics-tools-py",
      "package_dir" :  { "": "lib/"},
      "packages": [ "comoonics.tools" ],
#      "py_modules" :   [ "comoonics.AutoDelegator", 
#                       "comoonics.lockfile",
#                       "comoonics.odict",
#                       "comoonics.stabilized",
#                       "comoonics.XMLConfigParser",
#                       "comoonics.ComSystemInformation" ],
      "scripts":       [ "bin/stabilized", "bin/com-sysreport", "bin/com-sysinfo" ],
    },
    "mgrep": {
      "name":"mgrep",
      "version":"0.1",
      "description":"com.oonics base tools",
      "long_description":""" 
com.oonics basic tools written in Python

Those are classes used by more other packages.
""",
      "url":"http://www.comoonics.org/development/mgrep",
      "scripts":       [ "bin/mgrep" ],
      "data_files":    [ ("share/man/man1",[ "man/mgrep.1.gz" ]) ],
    },
}

basedict=None
if setup_cfg.has_key(sys.argv[1]):
    basedict=setup_cfg[sys.argv[1]]
    sys.argv.remove(sys.argv[1])
elif setup_cfg.has_key(sys.argv[0]):
    basedict=setup_cfg[sys.argv[0]]
basedict["license"]="GPLv2+"
basedict["cmdclass"]={"bdist_rpm": bdist_rpm_fedora, "test": test}
#buildmanpages(basedict)
setup(**basedict)
