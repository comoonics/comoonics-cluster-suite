import sys
import os

sys.path.append("../lib")



from ComUtils import *
one="1"

lines=["eine eins", "eine zwei", "keine drei"]
print grepInLines(lines, "^eine (.*)")

if isInt(one):
    print( one+" is int")
if isInt("sds"):
    print("sds is not an int")
