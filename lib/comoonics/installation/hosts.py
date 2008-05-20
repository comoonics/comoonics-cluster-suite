# hosts.py: simple implementation of reading and writing hostsfiles
#
# Andrea Offermann <offermann@atix.de>
#
# Copyright 2008 ATIX Informationstechnologie und Consulting AG
#
# This software may be freely redistributed under the terms of the GNU
# library public license.
#
# You should have received a copy of the GNU Library Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
import re

class HostsFile:
    def __init__(self):
        self._ips=dict()
        self._names=dict()
        self.lines=list()
        self._iplines=dict()
    
    def addHost(self, _ip, _names, noline=False):
        if isinstance(_names, basestring):
            _names=[ _names ]
        _ipnames=list()
        for _name in _names:
            if not self._names.has_key(_name):
                self._names[_name]=_ip
                _ipnames.append(_name)
            elif self._names[_name]!=_ip:
                del self.lines[self._ips[_name]]
                #del self._ips[_name]
                noline=False
                self._names[_name]=_ip
                _ipnames.append(_name)
        if not self._ips.has_key(_ip):
            self._ips[_ip]=_ipnames
        else:
            noline=False
            del self.lines[self._iplines[_ip]]
            self._ips[_ip].extend(_ipnames)
            _ipnames=self._ips[_ip]
        if not noline:
            self._iplines[_ip]=len(self.lines)
            self.lines.append("%s\t %s\n" %(_ip, " ".join(_ipnames)))
    def getHostByName(self, _name):
        return self._names[_name]
    def getHostByIp(self, _ip):
        return self._ips[_ip]
    def save(self, _outstream):
        for _line in self.lines:
            _outstream.write(_line)

def removeComments(_line):
    if _line.endswith("\n"):
        _line=_line[:-1]
    return re.sub("#.*$", "", _line)

def parse(_instream):
    """
    Returns a HostsFile instance
    """
    _hosts=HostsFile()
    _lineparser=re.compile("\s*(?P<ipaddress>[0-9.]+)\s+(?P<names>.*)$")
    _splitnames=re.compile("\s+")
    for _line in _instream:
        _hosts.lines.append(_line)
        _line=removeComments(_line)
        _match=_lineparser.search(_line)
        if _match:
            _hosts.addHost(_match.group("ipaddress"), _splitnames.split(_match.group("names")), True)
    return _hosts

def save(_hosts, _file):
    _hosts.save(_file)
def write(_hosts, _file):
    save(_hosts, _file)

def test():
    import sys
    _hostsfile=parse(open("/etc/hosts"))
    _hostsfile.addHost("172.16.0.100", "testserver")
    _hostsfile.addHost("172.16.0.101", ["testserver2", "testserver2.mydomain"])
    _hostsfile.addHost("172.16.0.101", "testserver3.mydomain")
    write(_hostsfile, sys.stdout)

if __name__ == "__main__":
    test()

######################
# $Log