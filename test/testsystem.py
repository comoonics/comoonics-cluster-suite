import sys
import os

sys.path.append("../lib")



from ComSystem import *

cmd1='echo "hallo stdout"'
cmd2='echo "hallo stderr" >&2'

print execLocalGetResult(cmd1)
print execLocalGetResult(cmd2, True)
