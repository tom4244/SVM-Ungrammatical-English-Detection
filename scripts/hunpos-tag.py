#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" tag text using Hunpos Tagger
    tagged file will be filename.tag
"""
import nltk, re, sys
from nltk.tag.hunpos import HunposTagger
textfile = sys.argv[1]
tagfilename = sys.argv[1] + '.tag'
sentences=open(textfile).read().split("\n")
tagfile=open(tagfilename, "w")
tagger = HunposTagger('english.model', 'hunpos-tag')
quotes = re.compile(r'\(\'([^ ]+?)\'\, \'([^ ]+?)\'\)')
punctuation = re.compile(r'\(([^ ]+)([.,!:;\'"]) ([^ ]+)\)')
taggedtext = ""
for sentence in sentences:
    tagged = tagger.tag(sentence.split())
    for word in tagged:
        taggedtext = taggedtext + str(word)
    # Remove extraneous quotes from tagging
    taggedtext = quotes.sub(r'(\1 \2)', taggedtext)
    # Separate punctuation from words and tag it
    taggedtext = punctuation.sub(r'(\1 \3)(\2 \2)', taggedtext)   
    tagfile.write(taggedtext)
tagfile.close()


