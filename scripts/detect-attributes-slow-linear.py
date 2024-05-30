#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Experiment with linear classifier (processing was slower than
    with RBF kernel with same or less accuracy).
"""
# import re, sys, nltk, pfp, numpy
import re, sys, nltk, numpy, string
from nltk.tag.hunpos import HunposTagger
# use abs path so subprocessing module PIPE can find them
model_path = '/home/tom/classes/Masters-project/code/english.model'
hunpos_path = '/home/tom/classes/Masters-project/code/hunpos-tag'
tagger = HunposTagger(model_path, hunpos_path)
# textfile = sys.argv[1]
textfile=open("btextfile.txt")
tagfile = open('btextfile.txt' + '.tag', "w")
reportfile = open("rptfile.txt", "w")
end_sentence = re.compile(r'\.\s+')
sentences = end_sentence.split(textfile.read())
# regex patterns to prepare and clean up hunpos-tagged text
punct = re.compile(r'([%s])' % re.escape(string.punctuation))
whtspace = re.compile(r'\s+')
tagged_punct = re.compile(r'\(([^ a-zA-Z0-9])\s[^ ]+\)')
quotes = re.compile(r'\([\'\"]([^ ]+?)[\'\"]\, [\'\"]([^ ]+?)[\'\"]\)')
tagged_text = ""
for sentence in sentences:   
    sentence = sentence + ' .\n'
    # separate punctuation as individual token
    sentence = punct.sub(r' \1 ', sentence)
    # remove extra whitespace
    sentence = whtspace.sub(r' ', sentence)
    # tag with Hunpos tagger
    tagged = tagger.tag(sentence.split())
    tagged_sentence = ""
    for word in tagged:
        tagged_sentence = tagged_sentence + str(word)
    tagged_text = tagged_text + tagged_sentence + '\n'
# remove quotes from tagger for better readability
tagged_text = quotes.sub(r'(\1 \2)', tagged_text)
# make tag of punctuation to be same char as punctuation
# instead of random tags
tagged_text = tagged_punct.sub(r'(\1 \1)', tagged_text)
tagfile.write(tagged_text)

class Word:
    spelling = []
    tag = []
    number = 0
    spelling_context = [None, None, None, None, None]
    tag_context = [None, None, None, None, None]
   
word_tag_ptn = re.compile(r'\((\S+) (\S+)\)')   
word = []
wordcount = 0
tags = []
# attach spelling, tag, number for each word
for word_tag in word_tag_ptn.finditer(tagged_text):
    thisword = Word()
    thisword.number = wordcount
    thisword.tag = word_tag.group(2)
    tags.append(word_tag.group(2))
    thisword.spelling = word_tag.group(1)
    word.append(thisword)
    wordcount = wordcount + 1
# words.append(m.group(2))
# print '%s %s %s' % (word[4].number, word[4].spelling, word[4].tag)
print('%s words read' % (wordcount))
tagfile.close()
textfile.close()
# parsefile.close()

def print_attribute(name, next_one, direction):
    """ print out a grammatical attribute detected/measured for a word """
    global word_number
    sys.stdout.write('"%s" attribute at %s: "' % 
                    (name, word[word_number].number))
    if direction == 'forward':
        for item in range(word_number-1, next_one+2):
            sys.stdout.write('%s ' % (word[item].spelling))
    else:
        for item in range(next_one-1, word_number+2):
            sys.stdout.write('%s ' % (word[item].spelling)) 
    print('"')
   
word_number = 0

"""
Parse grammatical attribute check instructions written in English
 For example, to check for 'many' followed by a singular noun:
   check("Attribute: 'determiner sing/plur'. 
   From 'many' check forward 8 words for ['NNP', 'NN']. 
   But stop looking if ['NNS', 'NNPS'] are found first.)
 For details, please see the User's Guide
"""
def check(instructions):
    """ check word based on its part of speech for grammatical
        attributes using hand-written rules
    """
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
        # print 'before split, start-if is %s' % (type(start_if))      
        start_if = start_if.split() #converts to list
    elif re.search(r'[Ff]rom \[', find) != None:
        start_if = eval(re.search(r'[Ff]rom (\[.+\]) ', find).group(1))
    else:
        print("format error in instructions")
    if 'forward' in find:
        direction = 'forward'
    elif 'backward' in find:
        direction = 'backward'
    else:
        print("format error in forward/backward of instructions")
    # print('start_if is %s; type %s; direction is %s' % 
    #     (start_if, type(start_if), direction))
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
        print("format error in second line of instructions")
    if re.search(r'[Nn]o stop condition', abort) != None:
        early_stop = 'no stop condition'
    elif re.search(r' if .*\[', abort) != None:
        early_stop = eval(re.search(r' if .*(\[.+\])', abort).group(1))
    elif re.search(r" if .*'", abort) != None:
        early_stop = re.search(r" if .*('.+')", abort).group(1)
        early_stop = early_stop.split() #converts to list
    else:
        print("format error in third line of instructions")
    if re.search(r'last in a sequence', find) != None:
        sequence = True
    else:
        sequence = False
    # print('%s %s %s %s' % (start_if, depth, early_stop, target))
    for item in start_if:
        # if item == 'an':
            # print('start-if is %s; item is %s; word-spelling is %s' % \)
            # (start_if, item, word[word_number].spelling)
        if word[word_number].tag == item or 
            word[word_number].spelling.lower() == item:
            if direction == 'backward':
                begin, end, step = word_number-1, word_number-depth-1, -1
            else:
                begin, end, step = word_number+1, word_number+depth+1, 1
            if begin < 0: begin = 0
            if end > wordcount: end = wordcount            
            for next_one in range(begin, end, step):
                # early stop condition check
               if early_stop != 'no stop condition' and 
                   (word[next_one].tag in early_stop or 
                   word[next_one].spelling.lower() in early_stop):
                   # hprint('early_stop condition %s reached from \'%s\', %s' % 
                   # (early_stop, word[word_number].spelling, word_number))
                   break
               # negative condition check 
               if re.search(r' for no ', find) != None and 
                   (word[next_one].spelling.lower() in target or 
                   word[next_one].tag in target):
                   break # no attribute; negative condition satisfied
               # sequence check; move to the end of the sequence
               # only left-to-right sequences are currently supported
               if sequence == True:
                   if word[next_one].tag in target or 
                       word[next_one].spelling.lower() in target:                      
                       while word[next_one].tag in target or 
                           word[next_one].spelling.lower() in target:
                           next_one += 1
                       next_one -= 1
               # condition checks   
               if (target == 'starting vowel sound' and 
                   item == 'a' and 
                   word[next_one].spelling.lower().startswith in 
                   ['a', 'e', 'i', 'o', 'u']) or 
                   (target == 'starting consonant sound' and 
                   item == 'an' and 
                   word[next_one].spelling.lower().startswith not in 
                   ['a', 'e', 'i', 'o', 'u']) or 
                   word[next_one].tag in target or 
                   word[next_one].spelling.lower() in target:
                       print_attribute(attribute_name, next_one, direction)
                       break
               # negative condition check continued
               if re.search(r' for no ', find) != None:
                   if (direction == 'backward' and next_one == end+1) or 
                       next_one == end-1:
                       print_attribute(attribute_name, next_one, direction)
         
def adj_ord():   
    """ Check for 'many' followed by a singular noun.
        Example: 'I don't have many carrot.'
    """
    global word_number
    check("Attribute: 'determiner sing/plur'. 
        From 'many' check forward 8 words for ['NN', 'NNP']. 
        But stop looking if tags ['NNS', 'NNPS'] are found first.")

def determ(): 
    """ Attributes based on determiners """
    global word_number
    # Check for 'a' followed by vowel sound.
    # Example: 'I don't have a eraser.'
    check("Attribute: 'determiner a/an vowel/cons'. 
        From 'a' check forward 1 word for starting vowel sound. 
        No stop condition.")
    # check for 'an' followed by consonant sound
    check("Attribute: 'determiner a/an vowel/cons'. 
        From 'an' check forward 1 word for starting consonant sound. 
        No stop condition.")
    # check for 'a, an, this, or that' followed by plural noun
    # example: 'She doesn't like a train station dogs.'
    check("Attribute: 'article sing/plur'.
        From ['a', 'an', 'this', 'that'] check forward 8 words for 
        the last in a sequence of ['VBG', 'NN', 'NNP', 'NNS', 'NNPS']. 
    But ignore it if ['NN', 'NNP'] are at the end of the sequence.")
    # check for 'some' instead of 'any' after a negative verb
    # example: 'He doesn't need some salt.'
    check("Attribute: 'determiner some/any'. 
        From 'some' check backward 6 words for ['not', \"n't\"]. 
        No stop condition.")
    # check for 'any' instead of 'some' after an affirmative verb
    # example: 'She asked for any money'
    check("Attribute: 'determiner some/any'. 
        From 'any' check backward 4 words for no ['not', \"n't\"]. 
        No stop condition.")

def noun():
    """ Attributes based on nouns """
    # Check for articles before proper nouns.
    # Example: 'The Bob is a friend of mine.'
    check("Attribute: 'determiner with proper noun'. 
        From ['NNP', 'NNPS'] check backward 8 words for ['a', 'an', 'the']. 
        But ignore it if ['NN', 'NNS'] are seen first.")

def prep():
    """ Attributes based on prepositions """
    # print 'the prep is %s' % (word[word_number].spelling)
    pass

def verb():
    """ Check for 'agree' not followed by 'with', 'to', or 'that'. """
    global word_number
    check("Attribute: 'preposition missing'. 
    From 'agree' check forward 2 words for no ['with', 'to', 'that']. 
    No stop condition.")
    # print 'the verb is %s' % (word[word_number].spelling)

tags = {'DT':determ, 'IN':prep, 'JJ':adj_ord, 
        'NN':noun, 'NNP':noun, 'NNPS':noun, 'NNS':noun, 
        'VB':verb, 'VBD':verb, 'VBG':verb, 'VBP':verb, 
        'VBZ':verb }

checkwords = ["of", "in", "to", "for", "with", "on", "at", "by", "from", 
              "into", "about", "a", "an", "the", "this", "that", "these", 
              "those", "my", "your", "his", "its", "our", "their", "both", 
              "each", "either", "enough", "every", "all", "another", "any", 
              "few", "fewer", "less", "little", "many", "more", "most", 
              "much", "neither", "no", "other", "several", "some"]

# checkwords = ["from", "all"]
# sys.stdout = reportfile
matchlist = []
mislist = []
total_matches = 0
total_misses = 0
# sys.exit()
# pattern to improve report readability
quote_brkt = re.compile(r'[\'\,\[\]]')
for item in range(len(word)):
    # for each tagged word, do attribute check defined above 
    # corresponding to part of speech tag in 'tags' list above
    """
    if word[item].tag in tags:
        # tags[word[item].tag](word[item].number)
        word_number = word[item].number
        tags[word[item].tag]()
    """
    # for each tagged word, do attribute check using 5gram corpus
    # for the word's part of speech
    # get context for each word
    # item = 195   #for testing; 'island between Honshu'
    # print "the word is %s " % (word[item].spelling)
    if word[item].spelling in checkwords:   
        position = word[item].number
        test_word = word[item].spelling
        context = []
        tag_context = []
        if position == 0:
            # for i in range(0,3):    # 5gram on border
            for i in range(0,2):       # 3gram on border
                context.append(word[i].spelling)
                tag_context.append(word[i].tag)
            """      
            elif position == 1:
                for i in range(0,4):
                    context.append(word[i].spelling)
                    tag_context.append(word[i].tag)
            """
        elif position == wordcount - 1:
            # for i in range(wordcount - 3, wordcount):  # 5grams
            for i in range(wordcount - 2, wordcount):   # 3grams
                context.append(word[i].spelling)
                tag_context.append(word[i].tag)
            """      
            elif position == wordcount - 2:
                for i in range(wordcount - 4, wordcount - 1):
                    context.append(word[i].spelling)
                    tag_context.append(word[i].tag)
            """
        else:
            # for i in range(-2,3):   # 5grams
            for i in range(-1,2):    # 3grams
                context.append(word[position + i].spelling)
                tag_context.append(word[position + i].tag)

        #*********artificially injecting words here********
        #   test_word = 'that'
        #   context = ['-', '1', 'that', 'there', 'are']
        #****************************************************
        # print("Examining %s \n" % (context))
        tw_corpus = "word_corpuses/" + test_word + "_corpus"
        # Compare tag_context with 5grams in the word's corpus.
        # ('tw_corpus') and see if the usage is common; this
        # Implies there is no grammatical error.
        # If the usage is not there, try to classify the type of
        # error by POS pattern used or other method (TBD).
        corpus=open(tw_corpus)
        grams=corpus.read().split("\n")
        # Look for, say, three matches to the tag pattern used
        match = 0
        # TBD: as currently coded below, 4grams are ignored
        # tags = re.compile(r'\([^ ]+ ([^ ]+)\)\([^ ]+ 
        #     ([^ ]+)\)\([^ ]+ ([^ ]+)\)\([^ ]+ ([^ ]+)\)\([^ ]+ ([^ ]+)\)')
        # Search any 3 consecutive words & tags
        # group1: preword   grp2: pretag  grp3: test_word's tag
        # grp4: postword  grp5: posttag
        contxt_ptn = re.compile(r'\(([^ ]+) ([^ ]+)\)\('+test_word+' 
            ([^ ]+)\)\(([^ ]+) ([^ ]+)\)') 
        for line in grams:
            # linetxt = []
            t = contxt_ptn.search(line)
            if t:
                # Match the same word
                # All proper nouns match each other
                if (((t.group(1) == context[0]) or
                    (t.group(2) == ('NNP' or 'NNPS') and
                    (tag_context[0] == ('NNP' or 'NNPS')))) and
                    ((t.group(4) == context[2]) or
                    (t.group(5) == ('NNP' or 'NNPS') and
                    (tag_context[2] == ('NNP' or 'NNPS'))))):
                    # print line

                    """
                    # linetxt.append(t.group(1))
                    linetxt.append(t.group(2))
                    linetxt.append(t.group(3))
                    linetxt.append(t.group(4))
                    # linetxt.append(t.group(5))
                    if context == linetxt:
                       print "linetxt is %s " % (linetxt)
                       print "context is %s " % (context)
                    """
                    match = match + 1
                    if match > 1:
                        # print "matched more than 1"
                        matchlist.append(context)
                        quote_brkt = re.compile(r'[\'\,\[\]]')
                        print("match %s: %s" % \
                            (total_matches, quote_brkt.sub(r'', str(context))))
                        total_matches = total_matches + 1
                        break 
        if match == 0:
            # print("searched all lines; no match")
            mislist.append(context)
            print("MISS %s:                               %s" % 
                (total_misses, quote_brkt.sub(r'', str(context))))
            total_misses = total_misses + 1
reportfile.write("Matches:\n")
for m in matchlist:
    # reportfile.write(str(m) + "\n")
    reportfile.write(quote_brkt.sub('', str(m)) + "\n")
# reportfile.write(str(matchlist))
reportfile.write("\nMisses:\n")
for m in mislist:
    # reportfile.write(str(m) + "\n")   
    reportfile.write(quote_brkt.sub('', str(m)) + "\n")
# reportfile.write(str(mislist))
reportfile.flush()
reportfile.close()
# sys.stdout = sys._stdout_
                  
