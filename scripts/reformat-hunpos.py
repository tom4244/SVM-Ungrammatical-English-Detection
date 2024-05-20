#!/usr/bin/python3
# -*- coding: utf-8 -*-
# reformat hunpos tagged corpus output to nice list of 5grams
# also correct hunpos tags for single-character tokens like $
# the perl version of this was 4 times faster

import re, sys
hunpos_output = open("/home/tom/akb/cleaned-split-tagged",'r',1)
#hunpos_output = open("sample", 'r', 1)
newfile = open("entire_google_corpus", "w")
tagged_punct = re.compile(r'^(?P<single_char>[^ a-zA-Z0-9])\t(?P<tag>[^ ]+)\t')
wd_tag_pair = re.compile(r'^(\S+?)\s+(\S+?)\s+$')
sentence = ""
for word_tag in hunpos_output:   
   if (word_tag == "\n"):
      newfile.write(sentence + "\n")
      sentence = ""
   else:
      # avoid incorrectly tagged single-chars
      word_tag = tagged_punct.sub(r'\1\t\1\t', word_tag)
      # put in (word tag) form
      word_tag = wd_tag_pair.sub(r'(\1 \2) ', word_tag)
      sentence = sentence + word_tag   
newfile.close()
hunpos_output.close()
