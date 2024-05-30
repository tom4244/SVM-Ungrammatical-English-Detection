#!/usr/bin/python3
""" Compare pfp and Stanford POS tagging. """
#import sys, re
import re
pfile = open("stan-parser-parsed.txt")
# tfile = file("stan-pos-tagged.txt")
pfpfile = open("pfp-tagfile.txt")
parsed = pfile.read()
# tagged = tfile.read()
pfptagged = pfpfile.read()
pfile.close()
pfpfile.close()
# tfile.close()
# tag = re.sub(r'\w*_','',tagged).split()
parse = re.sub(r'\w*/','',parsed).split()
pfptag = re.sub(r' \S+\)','',pfptagged).split()
for w in range(len(parse)):
    print("%s %s" % (pfptag[w], parse[w]))

