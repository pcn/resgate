#!/usr/bin/env python

import json
import sys

import jmespath

# First arg is the jmespath file, second is the data
compiled_pth = jmespath.compile(open(sys.argv[1]).readline())
# print(compiled_pth)
print(compiled_pth.search(json.load(open(sys.argv[2]))))
