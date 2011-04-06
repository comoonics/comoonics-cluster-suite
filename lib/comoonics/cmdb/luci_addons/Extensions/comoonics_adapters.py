import cgi

def comoonicsControl(self, request):
    if request.REQUEST_METHOD == 'POST':
        return comoonicsControlPost(self, request)

    try:
        request.SESSION.set('checkRet', {})
    except:
        pass

    if 'ACTUAL_URL' in request:
        url = request['ACTUAL_URL']
    else:
        url = '.'

    if 'pagetype' in request:
        pagetype = request['pagetype']
    else:
        pagetype = '0'

    if 'type' in request:
        type=request['type']
    else:
        type="none"

    return comoonicsPortal(self, request, url, pagetype, type)

def comoonicsControlPost(self, request):
    if 'ACTUAL_URL' in request:
        url = request['ACTUAL_URL']
    else:
        url = '.'

    if 'type' in request.form:
        type = request.form['type']
    if 'pagetype' in request.form:
        pagetype = request.form['pagetype']
    else:
        try:
            request.SESSION.set('checkRet', {})
        except:
            pass
        return comoonicsPortal(self, request, '.', '0')

    try:
        validatorFn = formValidators[pagetype - 1]
    except:
        try:
            request.SESSION.set('checkRet', {})
        except:
            pass
        return comoonicsPortal(self, request, '.', '0')

    return comoonicsPortal(self, request, url, pagetype, type)

def comoonicsPortal(self, request=None, url=None, pagetype=None, type=None):
    ret = {}
    params=dict()
    left_tabs = [
       { "Title":       "RPM Search Source",
         "Description": "Com.oonics CMDB Software Management Search for RPMS.",
         "params":      { "pagetype":    "rpmsearch",
                          "searchfor" :  "source",
                          "type":        "cmdb"}
       },
       { "Title":       "Compare Souces by Category",
         "Description": "Com.oonics Compare Sources by Category.",
         "params":      { "pagetype":    "rpmcompare",
                          "searchfor" :  "category",
                          "type":        "cmdb" }
       },
       { "Title":       "Compare Sources 1:n",
         "Description": "Com.oonics Compare installed Sources by selecting one master and multiple nodes.",
         "params":      { "pagetype":    "rpmcompare",
                          "searchfor" :  "master",
                          "type":        "cmdb"}
       },
       { "Title":       "Compare Sources M:n",
         "Description": "Com.oonics Compare installed Sources comparing everything.",
         "params":      { "pagetype":    "rpmcompare",
                          "searchfor" :  "source",
                          "type":        "cmdb"}
       },
       { "Title":       "Systeminformations",
         "Description": "Com.oonics show information about Systems/Sources.",
         "params":      { "pagetype":    "systeminformation",
                          "searchfor" :  "systeminformation",
                          "type":        "cmdb"}
       },
       { "Title":       "Logs",
         "Description": "Com.oonics show logs about last changes.",
         "params":      { "pagetype":    "logs",
                          "searchfor" :  "logs",
                          "type":        "cmdb"}
       }
    ]
    cur = None

    pagetype = str(pagetype)

#
# The Add System page
#
    ret['curIndex'] = 0
    left_tabs[0]["currentItem"]=True
    for i in xrange(len(left_tabs)):
        tab=left_tabs[i]
        tab["absolute_url"]=url
        isCurrent=True
        for param in tab["params"].keys():
            isCurrent=isCurrent and tab.has_key("params") and tab["params"].has_key(param) and request.has_key(param) and tab["params"][param]==request[param]

        if isCurrent:
            cur = tab
            ret['curIndex'] = i
        tab["currentItem"]=isCurrent
        if tab["params"]:
            tab["absolute_url"]+="?"
            for paramk in tab["params"].keys():
                tab["absolute_url"]+=cgi.escape(paramk)+"="+cgi.escape(tab["params"][paramk])+"&"
    if cur and 'absolute_url' in cur:
        cur['base_url'] = cur['absolute_url']
    else:
        cur = {}
        cur['base_url'] = '#'

    ret['children'] = left_tabs
    return ret
