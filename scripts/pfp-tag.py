#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Part-of-speech tag text in a textfile using the pfp parser.
import nltk, re, sys, pfp, numpy
infile = sys.argv[1]
outfile = sys.argv[2]
# filename="ceejus-.txt"
textfile=open(infile)
tagfile=open(outfile, "w")
# sentences=textfile.read().split(". ")
sentences=textfile.read().split("\n")
counter=0
for sentence in sentences:
    if counter == 10:
        break
    counter = counter + 1
    print(sentence)
    # sentence = sentence + ". "
    parsed = pfp.Parser().parse(sentence)
    print(parsed)
    # Get tagged words from parsed tree
    # by trimming off parse tree's extra tags and parentheses
    trimmed = re.compile(r'\([^\s\(]+ [^\s\)]+\)')
    # Get each word and its tag
    pair_pattern = re.compile(r'\((\S+) (\S+)\)')
    for couple in trimmed.findall(parsed):
        tagfile.write(couple + ' ')
tagfile.close()
textfile.close()

