#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Check functioning of a new handwritten rule to
#   measure a linguistic feature

import re, sys, nltk, pfp, numpy
textfile=open("testfile3.txt")
#tagfile=open("pfp-tagfile.txt", "w")
tagfile = open("tagfile.txt", "w")
#parsefile=open("pfp-parsefile.txt", "w")
sentences=textfile.read().split(". ")
class Word:
   spelling = []
   tag = []
   number = 0
   spelling_5gram = ['','','','','']
   syntax_5gram = ['','','','','']
word = []
total_words = 0
for sentence in sentences:
  sentence = sentence + ". "
  """
  #tag with pfp
  parsed = pfp.Parser().parse(sentence)
  parsefile.write(parsed)
  #get tagged words from parsed tree
  # by trimming off parse tree's extra tags and parentheses
  trimmed = re.compile(r'\([^\s\(]+ [^\s\)]+\)')
  #get each word and its tag
  pair_pattern = re.compile(r'\((\S+) (\S+)\)')
  for couple in trimmed.findall(parsed):
#     sys.stdout.write(couple + " ")
     tagfile.write(couple + ' ')
"""
     #####put the Hunpos tagging here#####
     
  
     #attach spelling, tag, number for each word
     pair = pair_pattern.match(couple)
     if pair is not None:
        thisword = Word()
        thisword.number = total_words
        thisword.tag = pair.group(1)
#       tags.append(m.group(1))
        thisword.spelling = pair.group(2)
        word.append(thisword)
        total_words = total_words + 1
#       words.append(m.group(2))
#print '%s %s %s' % (word[4].number, word[4].spelling, word[4].tag)
print '%s words parsed' % (total_words)

#tagfile.write(str(tagged))
tagfile.close()
textfile.close()
#parsefile.close()

#print out a grammatical attribute detected/measured for a word
def print_attribute(name, next_one, direction):
   global word_number
   sys.stdout.write('"%s" attribute at %s: "' % \
                     (name, word[word_number].number))
   if direction == 'forward':
      for item in range(word_number-1, next_one+2):
         sys.stdout.write('%s ' % (word[item].spelling))
   else:
      for item in range(next_one-1, word_number+2):
         sys.stdout.write('%s ' % (word[item].spelling)) 
   print '"'
   
word_number = 0
"""
Parse grammatical attribute check instructions written in English
 For example, to check for 'many' followed by a singular noun:
   check("Attribute: 'determiner sing/plur'. \
   From 'many' check forward 8 words for ['NNP', 'NN']. \
   But stop looking if ['NNS', 'NNPS'] are found first.)
 For details, please see the User's Guide
"""
def check(instructions):
   #check word based on its part of speech for grammatical
   #attributes using hand-written rules
   global word_number
   instructions = instructions.split('. ')
   name = instructions[0]
   find = instructions[1]
   abort = instructions[2]
   in_quotes = re.compile(r'\'(.+)\'')
   in_brackets = re.compile(r'\[.+\]')
   attribute_name = in_quotes.search(name).group(1)
   if re.search(r'[Ff]rom here', find):
      start_if = word[word_number].spelling.lower().split() #always starts  
   elif re.search(r'[Ff]rom \'', find) != None:
      start_if = re.search(r'[Ff]rom \'(.+)\' ', find).group(1)
      #print 'before split, start-if is %s' % (type(start_if))      
      start_if = start_if.split() #converts to list
   elif re.search(r'[Ff]rom \[', find) != None:
      start_if = eval(re.search(r'[Ff]rom (\[.+\]) ', find).group(1))
   else:
      print "format error in instructions"
   if 'forward' in find:
      direction = 'forward'
   elif 'backward' in find:
      direction = 'backward'
   else:
      print "format error in forward/backward of instructions"
   #print 'start_if is %s; type %s; direction is %s' % (start_if, type(start_if), direction)      
   depth = int(re.search(r'(\d+) word', find).group(1))
   if re.search(r' for .*\[', find) != None:
      target = eval(re.search(r' for .*(\[.+\])', find).group(1))
   elif re.search(r'starting vowel sound', find) != None:
      target = 'starting vowel sound'
   elif re.search(r'starting consonant sound', find) != None:
      target = 'starting consonant sound'   
   elif re.search(r" for .*'", find) != None:
      target = re.search(r" for .*('.+')", find).group(1)
      target = target.split() #converts to list
   else:
      print "format error in second line of instructions"
   if re.search(r'[Nn]o stop condition', abort) != None:
      early_stop = 'no stop condition'
   elif re.search(r' if .*\[', abort) != None:
      early_stop = eval(re.search(r' if .*(\[.+\])', abort).group(1))
   elif re.search(r" if .*'", abort) != None:
      early_stop = re.search(r" if .*('.+')", abort).group(1)
      early_stop = early_stop.split() #converts to list
   else:
      print "format error in third line of instructions"
   if re.search(r'last in a sequence', find) != None:
      sequence = True
   else:
      sequence = False
   #print '%s %s %s %s' % (start_if, depth, early_stop, target)
   for item in start_if:
      #if item == 'an':
         #print 'start-if is %s; item is %s; word-spelling is %s' % \
           #(start_if, item, word[word_number].spelling)
      if word[word_number].tag == item or word[word_number].spelling.lower() == item:
         if direction == 'backward':
            begin, end, step = word_number-1, word_number-depth-1, -1
         else:
            begin, end, step = word_number+1, word_number+depth+1, 1
         if begin < 0: begin = 0
         if end > total_words: end = total_words            
         for next_one in range(begin, end, step):
            #early stop condition check
            if early_stop != 'no stop condition' and \
             (word[next_one].tag in early_stop or \
             word[next_one].spelling.lower() in early_stop):
               #print 'early_stop condition %s reached from \'%s\', %s' % \
                   #(early_stop, word[word_number].spelling, word_number)
               break
            # negative condition check 
            if re.search(r' for no ', find) != None and \
                   (word[next_one].spelling.lower() in target or \
                   word[next_one].tag in target):
                      break  #no attribute; negative condition satisfied
            # sequence check; move to the end of the sequence
            # only left-to-right sequences are currently supported
            if sequence == True:
               if word[next_one].tag in target or \
                word[next_one].spelling.lower() in target:                      
                  while word[next_one].tag in target or \
                   word[next_one].spelling.lower() in target:
                      next_one += 1
                  next_one -= 1
            # condition checks   
            if (target == 'starting vowel sound' and \
                   item == 'a' and \
                   word[next_one].spelling.lower().startswith in \
                   ['a', 'e', 'i', 'o', 'u']) or \
                 (target == 'starting consonant sound' and \
                   item == 'an' and \
                   word[next_one].spelling.lower().startswith not in \
                   ['a', 'e', 'i', 'o', 'u']) or \
                 word[next_one].tag in target or \
                 word[next_one].spelling.lower() in target:
                    print_attribute(attribute_name, next_one, direction)
                    break
            # negative condition check continued
            if re.search(r' for no ', find) != None:
               if (direction == 'backward' and next_one == end+1) or \
                 next_one == end-1:
                  print_attribute(attribute_name, next_one, direction)
         
def adj_ord():   
   #Check for 'many' followed by a singular noun
   #  example: 'I don't have many carrot.'
   global word_number
   check("Attribute: 'determiner sing/plur'. \
   From 'many' check forward 8 words for ['NN', 'NNP']. \
   But stop looking if tags ['NNS', 'NNPS'] are found first.")

def determ(): # attributes based on determiners
   #check for 'a' followed by vowel sound
   #  example: 'I don't have a eraser.'
   global word_number
   check("Attribute: 'determiner a/an vowel/cons'. \
   From 'a' check forward 1 word for starting vowel sound. \
   No stop condition.")
   #check for 'an' followed by consonant sound
   check("Attribute: 'determiner a/an vowel/cons'. \
   From 'an' check forward 1 word for starting consonant sound. \
   No stop condition.")
   #check for 'a, an, this, or that' followed by plural noun
   # example: 'She doesn't like a train station dogs.'
   check("Attribute: 'article sing/plur'.\
   From ['a', 'an', 'this', 'that'] check forward 8 words for \
     the last in a sequence of ['VBG', 'NN', 'NNP', 'NNS', 'NNPS']. \
   But ignore it if ['NN', 'NNP'] are at the end of the sequence.")
   # check for 'some' instead of 'any' after a negative verb
   #  example: 'He doesn't need some salt.'
   check("Attribute: 'determiner some/any'. \
   From 'some' check backward 6 words for ['not', \"n't\"]. \
   No stop condition.")
   # check for 'any' instead of 'some' after an affirmative verb
   #  example: 'She asked for any money'
   check("Attribute: 'determiner some/any'. \
   From 'any' check backward 4 words for no ['not', \"n't\"]. \
   No stop condition.")

def noun():
   # check for article before proper noun
   #  example: 'The Bob is a friend of mine.'
   check("Attribute: 'determiner with proper noun'. \
   From ['NNP', 'NNPS'] check backward 8 words for ['a', 'an', 'the']. \
   But ignore it if ['NN', 'NNS'] are seen first.")

def prep():
   pass
   #print 'the prep is %s' % (word[word_number].spelling)

def verb():
   #check for 'agree' not followed by 'with', 'to', or 'that'
   global word_number
   check("Attribute: 'preposition missing'. \
   From 'agree' check forward 2 words for no ['with', 'to', 'that']. \
   No stop condition.")
   #print 'the verb is %s' % (word[word_number].spelling)

tags = {'DT':determ, 'IN':prep, 'JJ':adj_ord, 'NN':noun, \
        'NNP':noun, 'NNPS':noun, \
        'NNS':noun, 'VB':verb, 'VBD':verb, 'VBG':verb, 'VBP':verb, \
        'VBZ':verb }

# for each tagged word, do attribute check defined above 
#  corresponding to part of speech tag in 'tags' list above
for item in range(len(word)):
   if word[item].tag in tags:
      #tags[word[item].tag](word[item].number)
      word_number = word[item].number
      tags[word[item].tag]()

#for each tagged word, do attribute check using 5gram corpus
# for the word's part of speech
