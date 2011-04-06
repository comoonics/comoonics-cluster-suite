from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB
from comoonics.cmdb.Converter import getConverter
from comoonics.cmdb.Reports import getReport
from comoonics.cmdb.ComSource import Source
from comoonics.db.ComDBLogger import DBLogger
#from OFS import SimpleItem
import ComoonicsGlobals
import cStringIO
try:
    from zLOG import LOG, INFO, DEBUG
except ImportError:
    LOG=ComoonicsGlobals.mylog.debug
    INFO=ComoonicsGlobals.mylog.info
    DEBUG=ComoonicsGlobals.mylog.debug

#class ComoonicsCMDBAllowModule (SimpleItem.SimpleItem):
#
#            "This module allows to use ComoonicsCMDB in Zope scripts"
#
#            meta_type = 'ComoonicsCMDBAllowModule'
#
#            def __init__(self, id):
#                "initialise a new instance of ComoonicsCMDBAllowModule"
#                self.id = id
#
#            def index_html(self):
#                "used to view content of the object"
#                return '<html><body>ComoonicsCMDBAccess is now enabled</body></html>'
#
#def manage_addComoonicsCMDBAllowModule(self, id, RESPONSE=None):
#            "Add a ComoonicsCMDBAllowModule to a folder."
#            self._setObject(id, ComoonicsCMDBAllowModule(id))
#            RESPONSE.redirect('index_html')
#
#def manage_addComoonicsCMDBAllowModuleForm(self):
#            "The form used to get the instance' id from the user."
#            return """<html>
#            <body>
#            Please type the id of the AllowComoonicsCMDB instance:<br>
#            <form name="form" action="manage_addComoonicsCMDBAllowModule"><br>
#            <input type="text" name="id"><br>
#            <input type="submit" value="add">
#            </form>
#            </body>
#            </html>"""

def getMyattr(theclass, name, default=None):
    if hasattr(theclass, name):
#        mylog.debug("%s.getMyattr(%s)=%s" %(theclass.__class__, name, getattr(theclass, name)))
        return getattr(theclass, name)
    elif type(theclass)==dict and theclass.has_key(name):
#        mylog.debug("%s.getMyattr(%s)=%s" %(theclass.__class__, name, theclass[name]))
        return theclass[name]
    else:
#        ComoonicsGlobals.mylog.debug("%s.getMyattr(%s)=%s" %(theclass.__class__, name, default))
        return default

def getSourcesAsSystemInformation(searchstring=None):
    ComoonicsGlobals.mylog.debug("getSourcesAsSystemInformation")
    source=Source(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
    sources=source.getSourcesAsSysteminformations(searchstring)
    for i in range(len(sources)):
        setattr(sources[i], "cssid", ComoonicsGlobals.installed_ids[i%len(ComoonicsGlobals.installed_ids)])
    del source
    return sources

def getColnamesForSystemInformation():
    ComoonicsGlobals.mylog.debug("getColnamesForSystemInformation")
    return [ "name", "type", "kernelversion", "uptime", "lastimport"]

def getSourcesForCMDB():
#    return ["name1", "name2", "name3"]
    cmdb=SoftwareCMDB(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
    clusters=cmdb.getClusters()
    cmdb.db.close()
    del cmdb
    return clusters

def getCategoriesForCMDB():
#    cmdb=SoftwareCMDB(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
#    return cmdb.getClusters()
#    mylog.info("testlogging2")
#    LOG("ComoonicsCMBD", INFO, "testlogging2 handlers: %s" %(logging._handlers))
    source=Source(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
    categories=source.getCategories()
    source.db.close()
    del source
    return categories

def createConverter(source=None, master=None, category=None, where=None, convertertype="coladddiffs/dict"):
    cmdb=SoftwareCMDB(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
    ComoonicsGlobals.mylog.debug("searching for master %s with source %s" %(master, source))
    if category:
        dbsource=Source(dbhandle=cmdb.db)
        source=dbsource.getSourcesForCategory(category)
        ComoonicsGlobals.mylog.debug("got %u sources for category %s" %(len(source), category))
    if isinstance(source, basestring):
        source=[source]
    packages=cmdb.getPackages(source, master, None, 0, 0, where)
    differences=packages.differences()
    ComoonicsGlobals.mylog.debug("Searching for converter: %s" %convertertype)
    converter=getConverter(convertertype)(differences)
    ComoonicsGlobals.mylog.debug("Got converter: %s" %converter)
    return converter
        
def createReport(source=None, master=None, category=None, where=None, reporttype="diffs/text/csv"):
    cmdb=SoftwareCMDB(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
    ComoonicsGlobals.mylog.debug("searching for master %s with source %s" %(master, source))
    if category:
        dbsource=Source(dbhandle=cmdb.db)
        source=dbsource.getSourcesForCategory(category)
        ComoonicsGlobals.mylog.debug("got %u sources for category %s" %(len(source), category))
    if isinstance(source, basestring):
        source=[source]
    packages=cmdb.getPackages(source, master, None, 0, 0, where)
    differences=packages.differences()
    ComoonicsGlobals.mylog.debug("Searching for converter: %s" %reporttype)
    report=getReport(reporttype)(differences)
    ComoonicsGlobals.mylog.debug("Got converter: %s" %report)
    return report
        
def getSoftwareForCMDBSearch(source, packagesearch, limitfrom=0, limitlength=20, searchfor="source", master=None, details=None, convertertype="coladddiffs/dict"):
    details_bool=getDetailBools(details, searchfor)
    ComoonicsGlobals.mylog.debug("details_bool: %s" %(details_bool))

    if limitfrom < 0:
        limitfrom=0
#    ret_rs=list()
    where=None
    if packagesearch and packagesearch != "":
        where=["name LIKE \"%"+packagesearch+"%\""]
    
    ComoonicsGlobals.mylog.debug("searchstring: %s" %packagesearch)
    if searchfor=="category":
        converter=createConverter(category=source, where=where, convertertype=convertertype)
    elif searchfor=="master" and master:
        converter=createConverter(source=source, master=master, where=where, convertertype=convertertype)
    elif searchfor=="source" and source and type(source)==list:
        converter=createConverter(source=source, where=where, convertertype=convertertype)
    elif searchfor=="source" and source and isinstance(source, basestring):
        converter=createConverter(source=source, where=where, convertertype=convertertype)
    else:
        pass

#    if not rs:
#        return None
#    rows=rs.fetch_row(limitlength, 1)
#    i=0
#    for row in rows:
#        ret_row=dict()
#        id=None
#        allinstalled=row.has_key(SoftwareCMDB.DIFFS_COLNAME)
#        for colname in row.keys():
#            if not colname==SoftwareCMDB.DIFFS_COLNAME:
#                ret_row[colname]=row[colname]
#            if colname==SoftwareCMDB.DIFFS_COLNAME:
#               id="%s_%s_%u" %(SoftwareCMDB.DIFFS_COLNAME, row[colname], i%2)
#           if row[colname]==SoftwareCMDB.NOT_INSTALLED_STRING and not allinstalled:
#               id=ComoonicsGlobals.notinstalled_ids[i%2]
#           elif not id and not allinstalled:
#                id=ComoonicsGlobals.installed_ids[i%2]
#        ret_row["id"]=id
#        ret_rs.append(ret_row)
#        i=i+1
#    cmdb.db.close()
#    del cmdb
    if converter:
        converter.convert(frompackage=limitfrom, topackage=limitfrom+limitlength, 
                          master=master, idcolname="id", idcolvalues=ComoonicsGlobals.notinstalled_ids,
                          iter=converter.packages.sort)
        ComoonicsGlobals.mylog.debug("Returning converter value %u, from %u..%u." %(len(converter.getvalue()), limitfrom, limitfrom+limitlength))
        return converter.getallvalues()
    else:
        ComoonicsGlobals.mylog.debug("Returning no converter.")
        return None

def exportSoftwareForCMDBSearchName(sourcename, searchstring, select="name", limitf=0, limitl=0, searchfor="source", mastername=None, details=None, sep=",", report="diffs/text/csv"):
    return exportSoftwareForCMDBSearch(sourcename, searchstring, select, limitf, limitl, searchfor, mastername, details, sep)
def exportSoftwareForCMDBSearch(sourcename, searchstring, select=None, limitf=0, limitl=0, searchfor="source", mastername=None, details=None, sep=",", report="diffs/text/csv"):
    if type(limitf)==str:
        limitf=int(limitf)
    if type(limitl)==str:
        limitl=int(limitl)

    where=None
    if searchstring and searchstring != "":
        where=["name LIKE \"%"+searchstring+"%\""]
    
    ComoonicsGlobals.mylog.debug("searchstring: %s" %searchstring)
    if searchfor=="category":
        _report=createReport(category=sourcename, where=where, reporttype=report)
    elif searchfor=="master" and mastername:
        _report=createReport(source=sourcename, master=mastername, where=where, reporttype=report)
    elif searchfor=="source" and sourcename and type(sourcename)==list:
        _report=createReport(source=sourcename, where=where, reporttype=report)
    elif searchfor=="source" and sourcename and isinstance(sourcename, basestring):
        _report=createReport(source=sourcename, where=where, reporttype=report)
    else:
        pass
    buffer=cStringIO.StringIO()
    if _report:
        _report.report(outputchannel=buffer, master=mastername, idcolname="id", idcolvalues=ComoonicsGlobals.notinstalled_ids,
                        iter=_report.packages.sort)
    else:
        ComoonicsGlobals.mylog.debug("Returning no report.")
    return buffer.getvalue()
#    rs=getSoftwareForCMDBSearch(sourcename, searchstring, limitf, limitl, searchfor, mastername, details)
#    firstLine=False
#    buf=""
#    ComoonicsGlobals.mylog.debug("Resolved %s lines; searchfor: %s"%(len(rs), searchfor))
#    if not select:
#        keys=getColumnNamesForCMDBSearch(sourcename, searchfor)
#    else:
#        keys=select
#    if isinstance(select, basestring):
#        keys=list()
#        keys.append(select)
#    for row in rs:
#        if not firstLine and not select:
#            buf+=sep.join(keys)
#            buf+="\n"
#            firstLine=True
#        rw=""
#        for key in keys:
#            rw+=row[key]+sep
#        rw=rw[:-1]
#        buf+=rw
#        buf+="\n"
#    return buf

def getDetailBools(mydetails, searchfor):
    _details=getDetailsForCMDBCompare(searchfor)
    if not ComoonicsGlobals.default_details.has_key(searchfor):
        return None
    if mydetails and isinstance(mydetails, basestring):
        _det=mydetails
        mydetails=list()
        mydetails.append(_det)
    bools=list(ComoonicsGlobals.default_details[searchfor])
    if not mydetails:
        return bools
    i=0
    for detail in _details:
        if detail in mydetails:
            bools[i]=not bools[i]
        i+=1
    return bools

def getDetailsForCMDBCompare(searchfor):
    if ComoonicsGlobals.details.has_key(searchfor):
        return ComoonicsGlobals.details[searchfor]
    else:
        return None

def getLogsFromSources(sources, searchstring="", limitfrom=0, limitlength=20):
    if limitfrom < 0:
        limitfrom=0
    ComoonicsGlobals.mylog.debug("getLogsFromSources: %s, %s, %s, %s." %(sources, searchstring, limitfrom, limitlength))
    dblog=DBLogger(hostname=ComoonicsGlobals.mysqlserver, user=ComoonicsGlobals.mysqluser, password=ComoonicsGlobals.mysqlpassword, database=ComoonicsGlobals.mysqldatabase)
    colnames=list(getColnamesForLogs(sources))
    colnames[0]="DATE_FORMAT(logtimestamp, '%Y%m%d%H%i%s') AS logtimestamp"
    _where="logsource=\"%s\"" %(sources)
    if searchstring and searchstring!="":
        _where+=" AND ( logmsg LIKE \"%%%s%%\" OR logexecinfo LIKE \"%%%s%%\")" %(searchstring, searchstring)
    rs=dblog.getLogs(sources, select=colnames, limit1=int(limitfrom), limit2=int(limitlength), order="logtimestamp DESC", where=_where)
    ret_rs=list()
    rows=rs.fetch_row(limitlength, 1)
    i=0
    for row in rows:
        ret_row=dict()
        for colname in row.keys():
            ret_row[colname]=row[colname]
        ret_row["cssid"]=ComoonicsGlobals.installed_ids[i%len(ComoonicsGlobals.installed_ids)]
        ret_rs.append(ret_row)
        i=i+1
    ComoonicsGlobals.mylog.debug("getLogsFromSources: Got %u logrows." %(len(ret_rs)))
    dblog.dbconnection.db.close()
    del dblog
    return ret_rs

def getColnamesForLogs(sources):
    return ComoonicsGlobals.log_cols

def parseRequest(request):
    if not request:
        return None
    import cgi
    query=request.environ["QUERY_STRING"]
    result=cgi.parse_qs(query)
    LOG('ComoonicsCMDB', INFO, "parsing: %s, %s"%(query, result))
    return result

def compareSourceNames(sourcename1, sourcenames2):
    if sourcename1 and sourcenames2:
        if type(sourcename1)==str and type(sourcenames2)==str:
            return sourcename1==sourcenames2
        elif type(sourcename1)==str and type(sourcenames2)==list:
            for sourcename2 in sourcenames2:
                if sourcename1 == sourcename2:
                    return True
        elif type(sourcename1)==list and type(sourcenames2)==str:
            for sname1 in sourcename1:
                if sname1 == sourcenames2:
                    return True
    # Else for all
    return False

#__all__ = ["getSourcesForCMDB"]
