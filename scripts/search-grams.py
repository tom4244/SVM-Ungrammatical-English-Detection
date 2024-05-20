#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Binary search a trigram corpus for a trigram
import re, sys, subprocess

filename = "acorpus"
file_sizes = {}
# shell out and 'wc' to quickly get lines in file
def file_len(fname):
    if file_sizes[fname]:
       return file_sizes[fname]
    p = subprocess.Popen(['wc', '-l', fname], 
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    result = int(result.strip().split()[0])
    file_sizes[fname] = result
    return result

target="(youth NN)(a DT)(great JJ)"
corpusfile = open(filename, 'r')
entries = file_len(filename)
print("Searching '%s' with %s entries." % (filename, entries))
width   = 64   # fixed width of an entry in the file padded with spaces
left, right = 0, entries-1 
thisgram = None
gram = re.compile(r'\(\S+?\s\S+?\)\(\S+?\s\S+?\)\(\S+?\s\S+?\)')
#print("The target is %s" % (target))
while thisgram != target and left <= right:
  mid = (left + right) / 2
  corpusfile.seek(mid * width)
  line = corpusfile.read(63)
  thisgram = gram.search(line)
  if thisgram:
     thisgram = thisgram.group(0)
  else:
     print("no match")
  if target > thisgram:
    left = mid + 1
  elif thisgram > target:
    right = mid - 1
  elif thisgram == target:
    print("Found '%s' on line %s" % (target, mid))
if thisgram != target:
  thisgram = None # for when search gram is not found
  print("Trigram '%s' not found in corpus" % (target))
corpusfile.close()

