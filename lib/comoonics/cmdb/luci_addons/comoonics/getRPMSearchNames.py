# Import a standard function, and get the HTML request and response objects.
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

from comoonics.cmdb.ComSoftwareCMDB import SoftwareCMDB

cmdb=SoftwareCMDB(hostname="mysql-server.gallien.atix", user="atix", password="atix", database="atix_cmdb")

return cmdb.getClusters()
