#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Stripped down classifier program for trying new handwritten rules
#import re, sys, nltk, pfp, numpy
import re, sys, nltk, numpy, string, subprocess, random
import yahoo_query, glob, os
from nltk.tag.hunpos import HunposTagger
from sklearn import svm
from operator import itemgetter

class Word:
   spelling = []
   tag = []
   number = 0
   sentence_nbr = 0

def tag_file(filename):
   # tag text file with Hunpos part-of-speech tagger
   # also populate Word class members and data
   global word, wordcount, sentence_list
   textfile=open(filename)
   # use abs path so subprocessing module PIPE can find them
   model_path = '/home/tom/classes/Masters-project/code/english.model'
   hunpos_path = '/home/tom/classes/Masters-project/code/hunpos-tag'
   tagger = HunposTagger(model_path, hunpos_path)
   #textfile = sys.argv[1]
   tagfile = open(filename + '_tag', "w")
   #sentences are expected to end with [.!?] and at least one space
   sentences = re.split(r'[\.!\?]\s+', textfile.read())
   # regex patterns to prepare and clean up hunpos-tagged text
   punct = re.compile(r'([%s])' % re.escape(string.punctuation))
   whtspace = re.compile(r'\s+')
   tagged_punct = re.compile(r'\(([^ a-zA-Z0-9])\s[^ ]+\)')
   quotes = re.compile(r'\([\'\"]([^ ]+?)[\'\"]\, [\'\"]([^ ]+?)[\'\"]\)')
   tagged_text = ""
   wordcount = 0
   word_tag_ptn = re.compile(r'\((\S+) (\S+)\)')
   sentence_list = []
   word = []
   for s_num, sentence in enumerate(sentences):   
      sentence = sentence + ' .\n'
      # separate punctuation as individual token
      sentence = punct.sub(r' \1 ', sentence)
      # remove extra whitespace
      sentence = whtspace.sub(r' ', sentence)
      # tag with Hunpos tagger
      tagged = tagger.tag(sentence.split())
      tagged_sentence = ""
      # make list of words of class Word
      # each tagged sentence ends with its sentence number
      for word_tag in tagged:
         # remove quotes from tagger for better readability
         word_tag = quotes.sub(r'(\1 \2)', str(word_tag))
         # make tag of punctuation to be same char as punctuation
         # instead of random tags
         word_tag = tagged_punct.sub(r'(\1 \1)', word_tag)
         tagged_sentence = tagged_sentence + word_tag
         w_t = word_tag_ptn.search(word_tag)
         thisword = Word()
         thisword.spelling = w_t.group(1)         
         thisword.tag = w_t.group(2)
         thisword.number = wordcount
         thisword.sentence_nbr = s_num
         word.append(thisword)
         wordcount = wordcount + 1
      tagged_text = tagged_text + tagged_sentence + str(s_num) + '\n'
      sentence_list.append(sentence)
   tagfile.write(tagged_text)
   tagfile.close()
   textfile.close()
   print("%s words read from '%s'" % (wordcount, filename))
   return(tagged_text)

#print out a grammatical attribute detected/measured for a word
def print_attribute(name, next_one, direction):
   global word, word_number, sentence_list, this_sentence, new_sentence
   if new_sentence:
      #reportfile.write("\nthis_sentence: %s   word: %s    word nbr: %s" % (this_sentence, word[word_number].spelling, word_number))
      #reportfile.write("   sentence list size: %s" % len(sentence_list))
      reportfile.write("\n%s\n" % (sentence_list[this_sentence]))
      new_sentence = False
   reportfile.write('"%s" attribute near "%s" (word %s): "' % \
                     (name, word[word_number].spelling, \
                     word[word_number].number))
   if direction == 'forward':
      for item in range(word_number-1, next_one+2):
         reportfile.write('%s ' % (word[item].spelling))
   else:
      for item in range(next_one-1, word_number+2):
         reportfile.write('%s ' % (word[item].spelling)) 
   reportfile.write('"\n')
   

def print_params(start_word, start_here):
   global word, word_number
   print("startword: %s  tag: %s  spelling: %s   start_here: %s\n" % (start_word, word[word_number].tag, word[word_number].spelling.lower(), start_here))

"""
Parse grammatical attribute check instructions written in English
 For example, to check for 'many' followed by a singular noun:
   check("Attribute: 'determiner sing/plur'. \
   From 'many' check forward 8 words for ['NNP', 'NN']. \
   But stop looking if ['NNS', 'NNPS'] are found first.)
 For details, please see the User's Guide
"""

def check_rule(instructions):
   # parse hand-written rules in English to 
   # check word for grammatical attributes
   # based on its part of speech 
   global word, word_number, wordcount
   instructions = instructions.split('. ')
   name_part = instructions[0]
   find_part = instructions[1]
   abort_part = instructions[2]
   in_quotes = re.compile(r'\'(.+)\'')
   in_brackets = re.compile(r'\[.+\]')
   attribute_name = in_quotes.search(name_part).group(1)
   phrase = []
   phrase_offset = 0
   seq_abort = []
   skips = []
   early_stop = []
   thisword = word[word_number].spelling
   # Establish starting word(s) for pattern
   if re.search(r'[Ff]rom here', find_part):
      start_here = word[word_number].spelling.lower().split() 
   elif re.search(r'[Ff]rom the phrase ', find_part):      
      phrase = re.search(r' the phrase ["\'](.+?)["\'] ', find_part).group(1)
      phrase = phrase.split()
      for n in enumerate(phrase):
         if word[word_number + n[0]].spelling != n[1]:
            return(False)
      start_here = phrase[0].split()
      phrase_offset = len(phrase) - 1
   elif re.search(r'[Ff]rom \'', find_part) != None:
      start_here = re.search(r'[Ff]rom \'(.+?)\' ', find_part).group(1)
      start_here = start_here.split() #converts to list
   elif re.search(r'[Ff]rom \[', find_part) != None:
      start_here = eval(re.search(r'[Ff]rom (\[.+?\]) ', find_part).group(1))
      #start_here = re.search(r'[Ff]rom (\[.+\]) ', find_part).group(1)  #warning: this produces a string! use eval to change to list!
   else:
      print("format error in instructions")
   # Establish pattern direction
   if 'forward' in find_part:
      direction = 'forward'
   elif 'backward' in find_part:
      direction = 'backward'
   else:
      print("format error in forward/backward of instructions")
   # Establish pattern length   
   #print('start_here is %s; type %s; direction is %s' % \
   #        (start_here, type(start_here), direction))
   length = int(re.search(r'(\d+) word', find_part).group(1))
   if re.search(r' for .*\[', find_part) != None:
      pattern_end = eval(re.search(r' for .*(\[.+\])', find_part).group(1))
   elif re.search(r'starting vowel sound', find_part) != None:
      pattern_end = '_SVS_'
   elif re.search(r'starting consonant sound', find_part) != None:
      pattern_end = '_SCS_'   
   elif re.search(r" for .*'", find_part) != None:
      pattern_end = re.search(r" for .*('.+')", find_part).group(1)
      pattern_end = pattern_end.split() #converts to list
   else:
      print("format error in second line of instructions")
   # Establish word or condition that would invalidate the attribute
   if re.search(r'[Nn]o stop condition', abort_part) != None:
      early_stop = 'no stop condition'
   elif re.search(r'.* end is +\[', abort_part) != None:
      early_stop = eval(re.search(r'.* end is +(\[.+\])', abort_part).group(1))
   elif re.search(r".* end is '", abort_part) != None:
      early_stop = re.search(r".* end is ('.+')", abort_part).group(1)
      early_stop = early_stop.split() #converts to list
   elif re.search(r' if .*\[', abort_part) != None:
      early_stop = eval(re.search(r' if .*(\[.+\])', abort_part).group(1))
   elif re.search(r" if .*'", abort_part) != None:
      early_stop = re.search(r" if .*('.+')", abort_part).group(1)
      early_stop = early_stop.split() #converts to list
   else:
      print("format error in third line of instructions")
   # Establish whether the word sought can come after several others
   if re.search(r'last in a sequence', find_part) != None:
      sequence = True
      if re.search(r'skipping +\[', abort_part) != None:
         skips = re.search(r"skipping +(\[.+?\])", abort_part).group(1)
      elif re.search(r'skipping +\'', abort_part) != None:
         skips = re.search(r"skipping +\'(.+?)\'", abort_part).group(1).split()
      if re.search(r'sequence contains +\[', abort_part) != None:
         seq_abort = re.search(r"sequence contains +(\[.+?\])", abort_part).group(1)
      elif re.search(r'sequence contains +\'', abort_part) != None:
         seq_abort = re.search(r"sequence contains +\'(.+?)\'", abort_part).group(1).split()
   else:
      sequence = False
   for start_word in start_here:
      # starting point for pattern can be a tag or a word
      if word[word_number].tag == start_word or \
             word[word_number].spelling.lower() == start_word:
         if direction == 'backward':
            begin, end, step = word_number-1, word_number-length-1, -1
         else:
            begin, end, step = word_number + phrase_offset + 1, \
                    word_number + phrase_offset + length + 1, 1
         if begin < 0: begin = 0
         if end > wordcount: end = wordcount            
         for this in range(begin, end, step):
            # sequence check; move to the end of the sequence
            # only left-to-right sequences are currently supported
            if sequence == True:               
               #print("pattern_end is %s" % (pattern_end))
               while word[this].spelling in skips:
                  this = this + 1
               if word[this].spelling in seq_abort:
                  break
               if word[this].tag in pattern_end or \
                word[this].spelling.lower() in pattern_end:
                  while word[this].tag in pattern_end or \
                        word[this].spelling.lower() in pattern_end:
                     this += 1
                     if word[this].spelling in seq_abort:
                        break 
                  this -= 1
                  """
                  # go back to the noun or abort if not found
                  while word[this].tag not in ['NN', 'NNP', 'NNS', 'NNPS', 'VBG']:
                     this -= 1
                     if this <= begin - 1:
                        break
                  if this <= begin - 1:
                     break
                  """
            #early stop condition or end-of-sentence check
            if early_stop != 'no stop condition' and \
             (word[this].tag in early_stop or \
             word[this].spelling.lower() in early_stop or \
             word[this].spelling == '.'):
               break # no match; found cancelling stop condition
            # negative condition check 
            if re.search(r' for missing ', find_part) != None and \
                   (word[this].spelling.lower() in pattern_end or \
                   word[this].tag in pattern_end):
                      break  #no match; negative condition satisfied
               # condition checks
            if (pattern_end == '_SVS_' and \
                         start_word == 'a' and \
                         word[this].spelling.lower()[0] in \
                         ['a', 'e', 'i', 'o', 'u']) or \
              (pattern_end == '_SCS_' and \
                         start_word == 'an' and \
                         word[this].spelling.lower()[0] in \
                                          string.ascii_letters and \
                         word[this].spelling.lower()[0] not in \
                                     ['a', 'e', 'i', 'o', 'u', 'h']) or \
              word[this].tag in pattern_end or \
              word[this].spelling.lower() in pattern_end:
                 # pattern succesfully matched; print out match
                 print_attribute(attribute_name, this, direction)
                 if attribute_name == 'determiner such':
                    print("begin: %s  end: %s  word[this]: %s  start-word: %s letter: %s\n" % (begin, end, word[this].spelling, start_word, word[this].spelling.lower()[0]))
                 return(True)
            # negative condition check continued
            if re.search(r' for missing ', find_part) != None:
               if (direction == 'backward' and this == end+1) or \
                 this == end-1:
                  # pattern successfully matched; print out match
                  print_attribute(attribute_name, this, direction)
                  return(True)
   return(False)

def adj():   
   #Check for 'many' followed by a singular noun
   #  example: 'I don't have many carrot.'
   global attr
   if check_rule("Attribute: 'many with sing noun'. \
    From 'many' check forward 8 words for ['NN', 'NNP']. \
    But stop looking if tags ['NNS', 'NNPS'] are found first."):
       attr['adj-many'] = attr['adj-many'] + 1

def adjcmp():
   # comparative adjective
   global attr
   pass

def adjsup():
   # superlative adjective
   global attr
   pass

def adv():
   # adverb, tag 'RB'
   global attr

   #Check for 'almost' used like 'most'
   #  example: 'Almost sea creatures are fish.'
   global attr
   if check_rule("Attribute: 'almost used like most'. \
   From 'almost' check forward 1 word for \
   ['JJ', 'NNS', 'NNPS']. No stop condition. "):
       attr['adv-almost'] = attr['adv-almost'] + 1
   """
   if check_rule("Attribute: 'almost used like most'. \
    From 'almost' check forward 1 word for missing \
     ['all', 'no', 'any', 'CD', 'anyone', 'anybody', 'never', 'always', 'JJ', 'DT']. \
    No stop condition."):
       attr['adv-almost'] = attr['adv-almost'] + 1   
   """
def advcmp():
   # comparative adverb
   global attr
   pass

def dtrm(): # attributes based on determiners 
   # such as a, an, the, this, that, each, every, no, all 
   # check for 'a' followed by vowel sound
   #  example: 'I don't have a eraser.'
   global attr
   if check_rule("Attribute: 'determiner a/an vowel/cons'. \
    From 'a' check forward 1 word for starting vowel sound. \
    But ignore it if \
           ['u', 'unesco', 'united', 'universal', 'utility', 'uniquely', \
           'university', 'uniform'] are found."):
       attr['dtrm-a'] = attr['dtrm-a'] + 1

   #check for 'an' followed by consonant sound
   #  example: 'I saw an big boat.'
   if check_rule("Attribute: 'determiner a/an vowel/cons'. \
    From 'an' check forward 1 word for starting consonant sound. \
    No stop condition."):
       attr['dtrm-an'] = attr['dtrm-an'] + 1

   # check for 'both of' followed by nouns.
   #  example: 'I talked with both of Joe and Bob.'
   if check_rule("Attribute: 'determiner both'. \
    From the phrase 'both of' check forward 1 word \
      for ['NN', 'NNS', 'NNP', 'NNPS']. \
    No stop condition."):
      attr['dtrm-both'] = attr['dtrm-both'] + 1

   #check for 'a, an, this, or that' followed by plural noun
   # possibly coming after adjectives and noun modifiers
   # also, adjust for known common tagging errors
   # example: 'She doesn't like a train station dogs.'
   if check_rule("Attribute: 'determiner sing/plur'. \
        From ['a', 'an', 'this'] check forward 1 word \
        but skipping ['VBG', 'JJ'] \
        for the last in a sequence of \
        ['NN', 'NNP', 'NNS', 'NNPS']. \
        But ignore it if the sequence contains \
        ['few', 'means', 'lot', 'using'], \
        or the end is \
        ['NN', 'NNP', 'centers', 'species', 'strikes', 'rhinoceros']. "):
       attr['dtrm-dsp'] = attr['dtrm-dsp'] + 1
   """
   if check_rule("Attribute: 'determiner sing/plur'. \
        From ['a', 'an', 'this'] check forward 1 word \
        for the last in a sequence of \
        ['NN', 'NNP', 'NNS', 'NNPS', 'JJ'] \
        going back to the last noun. \
        But ignore it if the sequence contains \
        ['few', 'means', 'lot', 'using'], \
        or the end is \
        ['NN', 'NNP', 'centers', 'species', 'strikes', 'rhinoceros']. "):
       attr['dtrm-dsp'] = attr['dtrm-dsp'] + 1
   """
   # need a separate rule like the one above for 'that' which
   #  allows for an adjective after that as in 'it isn't that good'

   # IMPROVE FALSE POSITIVES

   # check for 'some' instead of 'any' after a negative verb
   #  example: 'He doesn't need some salt.'
   if check_rule("Attribute: 'determiner some/any'. \
    From 'some' check backward 6 words for ['not', 't']. \
    No stop condition."):
       attr['dtrm-some'] = attr['dtrm-some'] + 1

   # soon GET RID OF FALSE POSITIVES

def noun():
   global attr

   # check for 'reason(s)' used ungrammatically
   #  Example: 'My reason to doing that is I want to.'
   if check_rule("Attribute: 'noun reasons'. \
    From ['reason', 'reasons'] check forward 2 words \
      for missing ['for', 'that', 'why', 'is', 'because']. \
    No stop condition."):
       attr['noun-reason'] = attr['noun-reason'] + 1

   # check for 'lot of' followed by singular instead of plural
   #  example: 'I bought a lot of thing today.'
   if check_rule("Attribute: 'noun sing/plur'. \
    From 'lot' check forward 6 words for 'NN'. \
    But ignore it if ['VBG', 'NNS'] are found."):
         attr['noun-sp'] = attr['noun-sp'] + 1

   # check for singular noun followed by wrong verb type
   #  example 'He like to bowl.'
   if check_rule("Attribute: 'noun subj-verb disagreement'. \
    From 'NN' check forward 1 word for 'VBP'. \
    No stop condition."):
         attr['noun-svdis'] = attr['noun-svdis'] + 1

   # check for 'thing' without a determiner
   #  Example: 'I wanted thing to fix the car.'
   if check_rule("Attribute: 'determiner noun'. \
    From ['thing', 'importance'] \
       check backward 3 words for missing ['DT', 'one', 'PRP$']. \
    No stop condition."):
       attr['dtrm-noun'] = attr['dtrm-noun'] + 1

def prep():
   global attr
   pass
   #print('the prep is %s' % (word[word_number].spelling)

def prnper():
   # personal pronoun
   global attr
   pass

def prnpos():
   # possessive pronoun
   global attr
   pass

def to():
   # the word 'to', tag 'TO'
   global attr
   pass

def verb():
   #check for 'agree' not followed by 'with', 'to', 'that', or ','
   # example: I agree this idea.
   global word_number, attr
   if check_rule("Attribute: 'preposition missing'. \
    From 'agree' check forward 2 words for missing \
    ['with', 'to', 'that', ',']. \
    No stop condition."):
       attr['verb-prp'] = attr['verb-prp'] + 1

   # check for missing verb after 'can'
   #  example: I can many miles.
   if check_rule("Attribute: 'verb missing'. \
    From 'can' check forward 3 words for missing \
    ['VB', 'VBD', 'VBP']. \
    No stop condition."):
       attr['verb-can'] = ['verb-can'] + 1
   #print('the verb is %s' % (word[word_number].spelling)

def whdtrm():
   # WH-determiner; can be that, what, whatever, which, whichever
   global attr
   pass

# Match part of speech code to functions to be run.
tags = {'DT':dtrm, 'IN':prep, 'JJ':adj, 'JJS':adjsup, \
        'JJR':adjcmp, \
        'NN':noun, 'NNP':noun, 'NNPS':noun, 'NNS':noun, \
        'PRP':prnper, 'PRP$':prnpos, 'RB':adv, 'RBR':advcmp, \
        'TO':to, 'VB':verb, \
        'VBD':verb, 'VBG':verb, 'VBP':verb, 'VBZ':verb, \
        'WDT':whdtrm }

# trigram attribute strings for each part of speech
tgm_tags = {'DT':'dtrm', 'IN':'prep', 'JJ':'adj', 'JJR':'adjcmp', \
            'JJS':'adjsup', 'NN':'noun', 'NNP':'noun', \
            'NNPS':'noun', 'NNS':'noun', \
            'PRP':'prnper', 'PRP$':'prnpos', 'RB':'adv', \
            'RBR':'advcmp', 'TO':'to', 'VB':'verb', \
            'VBD':'verb', 'VBG':'verb', 'VBP':'verb', 'VBZ':'verb', \
            'WDT':'whdtrm'}

checkwords = ["of", "in", "to", "for", "with", "on", "at", "by", "from", "into", "about", "a", "an", "the", "this", "that", "these", "those", "my", "your", "his", "her", "its", "our", "their", "both", "each", "either", "enough", "every", "all", "another", "any", "few", "fewer", "less", "little", "many", "more", "most", "much", "neither", "no", "other", "several", "some"]
#checkwords = ["from", "all"]

def apply_rules(yahoo_misslist):
   # for each sentence, for each tagged word in the sentence, 
   #  do attribute check (function) 
   #  corresponding to part of speech tag in 'tags' dictionary  
   #  precondition: trigram_corpus_check has been run
   global word, word_number, sentence_list, new_sentence
   global this_sentence
   reportfile.write("Grammar attributes found in the text:\n")
   last_sentence = None
   new_sentence = False
   for item in range(len(word)):
      this_sentence = word[item].sentence_nbr
      # if this is a new sentence, print(it and its trigrams
      if this_sentence != last_sentence:
         new_sentence = True
         for line in yahoo_misslist:
             c_chk_sentence = line[2]
             if c_chk_sentence == this_sentence:
                # print(sentence, unnatural note
                if new_sentence == True:
                   reportfile.write("\n%s\n" % sentence_list[this_sentence])
                reportfile.write("uncommon or unnatural trigram:  '%s'\n" \
                        % (line[1]))
                new_sentence = False
         last_sentence = this_sentence

      # run grammatical rules function based on part of speech
      if word[item].tag in tags:
         #tags[word[item].tag](word[item].number)
         #if len(word[item].spelling) > 1:
           word_number = word[item].number
           tags[word[item].tag]()

# use shell command 'wc' to quickly get lines in file
def file_len(fname):
    file_sizes = {}
    if file_sizes.get(fname, None):
       return file_sizes[fname]
    p = subprocess.Popen(['wc', '-l', fname], 
       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    result = int(result.strip().split()[0])
    file_sizes[fname] = result
    return result

def measure(documents):
   # measure attributes in documents
   #   and put measurements in 'result_dictionaries' 
   #   and 'X' for SVM input
   #global word, wordcount, sentence_list, this_sentence, new_sentence
   global yahoo_misslist, attr, reportfile
   result_dictionaries = []
   for filename in documents:
      #filename = "atextfile.txt"      
      yahoo_misslist = []
      # names of attributes; used to separate types
      #   for example 'dtrm' is part of all determiner attributes


      attr = dict.fromkeys(['adj-many', 'adj-tgm', 'adjcmp-tgm', \
               'adjsup-tgm', 'adv-almost', 'adv-tgm', 'advcmp-tgm', \
               'dtrm-a', \
               'dtrm-an', 'dtrm-both', \
               'dtrm-dsp', \
               'dtrm-noun', 'dtrm-some', \
               'dtrm-tgm', 'noun-reason', 'noun-sp', 'noun-svdis', \
               'noun-tgm', \
               'prep-tgm', \
               'prnper-tgm', 'prnpos-tgm', 'to-tgm', \
               'verb-can', 'verb-prp', 'verb-tgm', 'whdtrm-tgm'], 0)

      reportfile = open(filename + "_rpt", "w")
      reportfile.write("Grammatical analysis report for '%s' file.\n" % (filename))
      tagged_text = tag_file(filename)   
      #trigram_corpus_check(tagged_text, yahoo_db_only = True)  
      # write stamped yahoo_misslist to file for reference
      #yahoofile.write("%s\n" % (filename))
      #for row in yahoo_misslist:
      #   yahoofile.write("%s\n" % (row))
      #yahoofile.write("\n")
      apply_rules(yahoo_misslist)
      this_result = sorted(attr.iteritems(), key=itemgetter(0))
      reportfile.write("\nattribute dictionary: \n%s" % (this_result))
      reportfile.close()
      result_dictionaries.append(this_result) 
   #yahoofile.close()
   unscaled_X = []
   for row in range(len(result_dictionaries)):
      unscaled_X.append([v for (k,v) in result_dictionaries[row]])
   return(unscaled_X)

word_number = 0
wordcount = 0
sentence_list = []
this_sentence = 0
new_sentence = False
yahoo_misslist = []
yahoo_discarded = []
word = []
attr = {}
#yahoofile = open("yahoofile", "w")
maxes = []

test_document = ['nontranslated-docs/28e']

unscaled_X = measure(test_document)
print(unscaled_X)

