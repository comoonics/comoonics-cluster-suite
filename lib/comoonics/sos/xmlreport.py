from stat import ST_UID, ST_GID, ST_MODE, ST_CTIME, ST_ATIME, ST_MTIME, S_IMODE
from time import strftime, localtime, time

class XmlReport:
    def __init__(self):
        try:
            import xml.dom
        except:
            self.enabled = False
            return
        else:
            self.enabled = True
        _impl = xml.dom.getDOMImplementation()
        self.doc=_impl.createDocument(None, "sos", None)
        self.root = self.doc.documentElement
        self.commands = self.doc.createElement("commands")
        self.root.appendChild(self.commands)
        self.files = self.doc.createElement("files") 
        self.root.appendChild(self.files)

    def add_command(self, cmdline, exitcode, stdout = None, stderr = None, f_stdout=None, f_stderr=None, runtime=None):
        if not self.enabled: return

        cmd = self.doc.createElement("cmd") 
        self.commands.appendChild(cmd)

        cmd.setAttribute("cmdline", cmdline)

        cmdchild = self.doc.createElement("exitcode")
        cmdchild.appendChild(self.doc.createTextNode(str(exitcode)))
        cmd.appendChild(cmdchild) 

        if runtime:
            cmdchild = self.doc.createElement("runtime")
            cmdchild.appendChild(self.doc.createTextNode(str(runtime)))
            cmd.appendChild(cmdchild)

        if stdout or f_stdout:
            cmdchild = self.doc.createElement("stdout")
            if stdout:
                cmdchild.appendChild(self.doc.createTextNode(stdout))
            if f_stdout:
                cmdchild.setAttribute("file", f_stdout)
            cmd.appendChild(cmdchild)

        if stderr or f_stderr:
            cmdchild = self.doc.createElement("stderr")
            if stderr:
                cmdchild.appendChild(self.doc.createTextNode(stderr))
            if f_stderr:
                cmdchild.setAttribute("file", f_stderr)
            cmd.appendChild(cmdchild)

    def add_file(self,fname,stats):
        if not self.enabled: return

        cfile = self.doc.createElement("file")
        self.files.appendChild(cfile)

        cfile.setAttribute("fname", fname)

        cchild = self.doc.createElement("uid")
        cchild.appendChild(self.doc.createTextNode(str(stats[ST_UID])))
        cfile.appendChild(cchild)
        cchild = self.doc.createElement("gid")
        cchild.appendChild(self.doc.createTextNode(str(stats[ST_GID])))
        cfile.appendChild(cchild)
        cchild = self.doc.createElement("mode")
        cchild.appendChild(self.doc.createTextNode(str(oct(S_IMODE(stats[ST_MODE])))))
        cfile.appendChild(cchild)
        cchild = self.doc.createElement("ctime")
        cchild.appendChild(self.doc.createTextNode(strftime('%a %b %d %H:%M:%S %Y', localtime(stats[ST_CTIME]))))
        cfile.appendChild(cchild)
        cchild.setAttribute("tstamp", str(stats[ST_CTIME]))
        cchild = self.doc.createElement("atime")
        cchild.appendChild(self.doc.createTextNode(strftime('%a %b %d %H:%M:%S %Y', localtime(stats[ST_ATIME]))))
        cfile.appendChild(cchild)
        cchild.setAttribute("tstamp", str(stats[ST_CTIME]))
        cchild = self.doc.createElement("mtime")
        cchild.appendChild(self.doc.createTextNode(strftime('%a %b %d %H:%M:%S %Y', localtime(stats[ST_MTIME]))))
        cfile.appendChild(cchild)
        cchild.setAttribute("tstamp", str(stats[ST_CTIME]))

    def serialize(self):
        import sys
        self.serialize_to_file(sys.stdout)

    def serialize_to_file(self,fname):
        if not self.enabled: return
        from xml.dom.ext import PrettyPrint

        if isinstance(fname, basestring):
            outfn = open(fname,"w")
        else:
            outfn=fname
        PrettyPrint(self.doc, outfn)
        if isinstance(fname, basestring):
            outfn.close()
