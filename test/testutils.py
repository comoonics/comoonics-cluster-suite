import sys
import os

sys.path.append("../lib")



from ComUtils import *
one="1"

if isInt(one):
    print( one+" is int")
if isInt("sds"):
    print("sds is not an int")
