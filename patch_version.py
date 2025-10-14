import os
import re
from gitonic.core.const import VERSION

with open("README.md") as f:
    c = f.read()

par = "VERSION[ /t]*=[ /t]*(.*)[ /t]*$"

matches = re.finditer(par, c, re.MULTILINE)

for m in matches:
    c = c.replace(m.groups()[0], VERSION)
    print("replaced", m.groups()[0])

with open("README.md", "w") as f:
    f.write(c)
