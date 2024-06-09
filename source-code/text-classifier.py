#!/usr/bin/python3
# -*- coding: utf-8 -*-
# text-classifier.py by Tom Box    
""" Classify grammatical errors in English text with a Support Vector Machine 
    with SVM features from handwritten rules and trigram analysis
"""
import re, sys, numpy, string, subprocess
import os, argparse
from nltk.tag.hunpos import HunposTagger
# import libsvm.svmutil
from libsvm.svm import *
# from sklearn.externals import joblib
import joblib
from operator import itemgetter

if os.path.exists("config.json"):
    import yahoo_query

class Word:
    spelling = []
    tag = []
    number = 0
    sentence_nbr = 0

def tag_file(path, filename):
    """ Tag text file with Hunpos part-of-speech tagger.
        Also populate Word class members and data.
    """
    global word, wordcount, sentence_list
    # textfile=file(path + "/" + filename)
    textfile = open(path + "/" + filename)
    # must use absolute path so subprocessing module PIPE can find them
    hmpath = os.getcwd()
    model_path = hmpath + '/english.model'
    hunpos_path = hmpath + '/hunpos-tag'
    tagger = HunposTagger(model_path, hunpos_path)
    tagfile = open(path + "/tag/" + filename + '_tag', "w")
    # sentences are expected to end with [.!?] and at least one space
    sentences = re.split(r'[.!?]\s+', textfile.read())
    # regex patterns to prepare and clean up hunpos-tagged text
    punct = re.compile(r'([%s])' % re.escape(string.punctuation))
    whtspace = re.compile(r'\s+')
    tagged_punct = re.compile(r'\(([^ a-zA-Z0-9])\s[^ ]+\)')
    quotes = re.compile(r'\([\'\"]([^ ]+?)[\'\"], [\'\"]([^ ]+?)[\'\"]\)')
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
    print("Analyzing '%s'" % (path + "/" + filename))
    return tagged_text

def yahoo_check(trigram, yahoo_threshold):
    """ Check trigrams not found in the trigram corpus with
        Yahoo limited web search. Trigrams with few occurences
        on the web may be part of ungrammatical or unnatural
        expressions.
    """
    global yahoo_misslist, yahoo_discarded, yahoo_db
    print_line = []
    word1, word2, word3 = trigram.split()
    # check for trigram in those previously retrieved from Yahoo
    #   as a low-occurence trigram before using Yahoo this time
    seen_before = False
    yahoo_db.seek(0)
    for line in yahoo_db:
        if trigram in line:
            # print "got %s from yahoo_db" % (trigram)
            seen_before = True
            ptn = re.search(r'\[\d+, u*\'(\d+)\', \'*(\d+)\'*, ', line)
            if ptn:
                yahoo_hits = ptn.group(1)
                rarity = ptn.group(2)
            else:
                print("the nonworking line is %s" % line)
    if not seen_before:
        # do yahoo search on word combination
        if not args.y:
            # option for documents measured before:
            #   instead of redoing a previously done search,
            #   return 99999 for searches already known
            #   to be over the threshold (only those under
            #   the threshold are saved in 'yahoo_db')
            yahoo_hits = 99999
        else:
            if not os.path.exists("config.json"):
                print("Yahoo trigram search option -y selected, ")
                print("but no config.json file found. ")
                print("See documentation for Yahoo BOSS setup.")
                sys.exit()
            print("Searching trigram with Yahoo limited web search")
            yahoo_hits = yahoo_query.get_web_uses("\"" + trigram + "\"")
        print_line.append(yahoo_hits)
        print_line.append(trigram)
        if int(yahoo_hits) > yahoo_threshold:
            yahoo_discarded.append(print_line)
            # just return False if it isn't very unusual
            return None, False
    # return hits if it seems to be an uncommon word combination
    return yahoo_hits, seen_before

def binary_search(searchtext, pattern, group_num, filename, linelength):
    """  Search file for an item using binary search.
         Search file must have lines of length linelength.
         Entire line containing search text is returned.
    """
    searchfile = open(filename, "r")
    entries = file_len(filename)
    left, right = 0, entries - 1
    file_text = None
    search_pat = re.compile(pattern)
    while file_text != searchtext and left <= right:
        mid = (left + right) / 2
        searchfile.seek(mid * linelength)
        line = searchfile.read(linelength - 1).strip()
        groups = search_pat.search(line)
        if groups:
            file_text = groups.group(group_num)
        else:
            print("regex pattern not matching lines in file")
            print("pattern is %s" % pattern)
            print("line is %s" % line)
        if searchtext > file_text:
            left = mid + 1
        elif file_text > searchtext:
            right = mid - 1
        elif file_text == searchtext:  # searchtext found in file
            searchfile.close()
            return line
    searchfile.close()
    if file_text != searchtext:  # searchtext not in file
        return None

def trigram_corpus_check(tagged_text):
    """ Search for trigram in local corpus made from Google 5gram corpus.
        Those not found could be ungrammatical and will be checked with
        the Yahoo limited web search.
    """
    global reportfile, attr, yahoo_misslist, yahoo_discarded, yahoo_db
    # match all trigrams, overlapping to start from each word
    getgrams = re.compile(r'(\(\S+?\s\S+?\)) \
                         (?=(\(\S+?\s\S+?\)\(\S+?\s\S+?\)))')
    all_text_trigrams = getgrams.finditer(tagged_text)
    # match tagged trigram from line
    gram = re.compile(r'\(\S+?\s\S+?\)\(\S+?\s\S+?\)\(\S+?\s\S+?\)')
    # match comma
    comma = re.compile(r',')
    words_notags = re.compile(r'\((\S+?)\s\S+?\)\((\S+?)\s\S+?\) \
                             ((\S+?)\s\S+?\)')
    # match trigram middle word part of speech tag
    word2_pos = re.compile(r'\(\S+?\s\S+?\)\(\S+?\s(\S+?)\)\(\S+?\s\S+?\)')
    matchlist = []
    yahoo_threshold = 1000
    total_checked = 0
    matched_google = 0
    uncommon_words = 0
    yahoo_discarded = []
    yahoo_db = open("yahoo_db", "a+")
    # freqfilename="../corpuses/Bing-frequency/Bing100k.txt.sorted5000-padded"
    freqfilename = "Bing100k.txt.sorted5000-padded"
    for n, item in enumerate(all_text_trigrams):
        tagged_trigram = item.group(1) + item.group(2)
        # tagged_trigram = item.group(0)
        # print "tagged_trigram is %s" % (tagged_trigram)
        grps = words_notags.search(tagged_trigram)
        word1 = grps.group(1)
        word2 = grps.group(2)  # main word, in the middle of the trigram
        word3 = grps.group(3)
        # only check trigrams with a word of interest in the middle
        if word2 in checkwords:
            # no commas in corpus; skip any trigram with commas
            if comma.search(tagged_trigram):
                continue
            total_checked = total_checked + 1
            # check the frequency of usage of the trigram words
            # before checking in trigram corpus and Yahoo
            too_rare = False
            w1_rarity = binary_search(word1.lower(),
                                      "(\S+) \d+", 1, freqfilename, 32)
            if w1_rarity is None:
                too_rare = True
                uncommon_words = uncommon_words + 1
            else:
                rarity1 = re.search(r'\S+ (\d+)', w1_rarity).group(1)
                w2_rarity = binary_search(word3.lower(), 
                        "(\S+) \d+", 1, freqfilename, 32)
                if w2_rarity is None:
                    too_rare = True
                    uncommon_words = uncommon_words + 1
                else:
                    rarity2 = re.search(r'\S+ (\d+)', w2_rarity).group(1)
            if not too_rare:
                word_rarity = max(rarity1, rarity2)
                filename = "word-corpuses/" + word2 + "_corpus"
                gram_pat = "\(\S+?\s\S+?\)\(\S+?\s\S+?\)\(\S+?\s\S+?\)"
                # note that the tagged trigram search is case-sensitive
                found = binary_search(tagged_trigram, gram_pat, 0, filename, 64)
                if found:
                    matched_google = matched_google + 1
                else:
                    sentence_nbr = word[n + 1].sentence_nbr
                    # trigram using common words was not found
                    #  in Google 5gram corpus; may be ungrammatical;
                    #  check how common usage is online with Yahoo
                    trigram = (word1 + " " + word2 + " " + word3)
                    yahoo_hits, seen_before = yahoo_check(trigram, yahoo_threshold)
                    if yahoo_hits:
                        print_line = []
                        print_line.append(sentence_nbr)
                        print_line.append(yahoo_hits)
                        print_line.append(word_rarity)
                        print_line.append(trigram)
                        yahoo_misslist.append(print_line)
                        if not seen_before:
                            # save to database of searches below threshold
                            yahoo_db.seek(0, 2)
                            yahoo_db.write(str(print_line) + "\n")
                        # keep track of possibly ungrammatical trigrams
                        #  for each part of speech
                        tag = word2_pos.search(tagged_trigram).group(1)
                        tgm_attr = tgm_tags[tag] + "-tgm"
                        attr[tgm_attr] = attr[tgm_attr] + 1
    yahoo_db.close()
    reportfile.write("\nPossible ungrammatical trigrams\n")
    reportfile.write("  (not found in common trigram corpus),\n")
    reportfile.write("  with sentence number in which they occured,\n")
    reportfile.write("  number of matches in Yahoo limited search,\n")
    reportfile.write("  and individual word rarity index (higher is rarer):\n\n")
    for line in yahoo_misslist:
        reportfile.write("{:>4} {:>5} {:>6} {:<40} \n".format(*line))
    reportfile.write("\nTrigrams not considered because they had more than %s \
                    Yahoo matches:\n\n" % yahoo_threshold)
    for line in yahoo_discarded:
        if line[0] == 99999:
            reportfile.write("             {:<40}\n".format(line[1]))
        else:
            reportfile.write("{:>12} {:<40}\n".format(*line))
    reportfile.write("\nUngrammatical trigram search summary:\n")
    reportfile.write("Total trigrams checked: %s\n" % total_checked)
    reportfile.write("Rarity caused by use of less common words: %s\n" % 
                     uncommon_words)
    reportfile.write("Found in common trigram corpus: %s\n" % 
                     matched_google)
    reportfile.write("Exceeded Yahoo hits threshold: %s\n" % 
                     (len(yahoo_discarded)))
    reportfile.write("Possibly ungrammatical (not in above categories): %s\n\n" \
                    % (len(yahoo_misslist)))

def print_attribute(name, next_one, direction):
    """ Print out a grammatical attribute detected/measured for a word."""
    global word, word_number, sentence_list
    reportfile.write('"%s" attribute near "%s" (word %s): \n"' % 
                     (name, word[word_number].spelling,
                      word[word_number].number))
    if direction == 'forward':
        begin = word_number - 3
        end = next_one + 4
        if begin < 0: begin = 0
        if end > wordcount: end = wordcount
        for item in range(begin, end):
            reportfile.write('%s ' % word[item].spelling)
    else:
        begin = next_one - 3
        end = word_number + 4
        if begin < 0: begin = 0
        if end > wordcount: end = wordcount
        for item in range(next_one - 3, word_number + 4):
            reportfile.write('%s ' % word[item].spelling)
    reportfile.write('"\n\n')

def check_rule(instructions):
    """ Parse handwritten rules in English to check word for 
        grammatical attributes based on its part of speech.
    """
    global word, word_number, wordcount
    instructions = instructions.split('. ')
    name_part = instructions[0]
    find_part = instructions[1]
    abort_part = instructions[2]
    in_quotes = re.compile(r'\'(.+)\'')
    in_brackets = re.compile(r'\[.+]')
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
                return False
        start_here = phrase[0].split()
        phrase_offset = len(phrase) - 1
    elif re.search(r'[Ff]rom \'', find_part) is not None:
        start_here = re.search(r'[Ff]rom \'(.+?)\' ', find_part).group(1)
        start_here = start_here.split()  # converts to list
    elif re.search(r'[Ff]rom \[', find_part) is not None:
        start_here = eval(re.search(r'[Ff]rom (\[.+?]) ', find_part).group(1))
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
    length = int(re.search(r'(\d+) word', find_part).group(1))
    if re.search(r' for .*\[', find_part) is not None:
        pattern_end = eval(re.search(r' for .*(\[.+])', find_part).group(1))
    elif re.search(r'starting vowel sound', find_part) is not None:
        pattern_end = '_SVS_'
    elif re.search(r'starting consonant sound', find_part) is not None:
        pattern_end = '_SCS_'
    elif re.search(r" for .*'", find_part) is not None:
        pattern_end = re.search(r" for .*('.+')", find_part).group(1)
        pattern_end = pattern_end.split()  # converts to list
    else:
        print("format error in second line of instructions")
    # Establish word or condition that would invalidate the attribute
    if re.search(r'[Nn]o stop condition', abort_part) is not None:
        early_stop = 'no stop condition'
    elif re.search(r'.* end is +\[', abort_part) is not None:
        early_stop = eval(re.search(r'.* end is +(\[.+])', abort_part).group(1))
    elif re.search(r".* end is '", abort_part) is not None:
        early_stop = re.search(r".* end is ('.+')", abort_part).group(1)
        early_stop = early_stop.split()  # converts to list
    elif re.search(r' if .*\[', abort_part) is not None:
        early_stop = eval(re.search(r' if .*(\[.+])', abort_part).group(1))
    elif re.search(r" if .*'", abort_part) is not None:
        early_stop = re.search(r" if .*('.+')", abort_part).group(1)
        early_stop = early_stop.split()  # converts to list
    else:
        print("format error in third line of instructions")
    # Establish whether the word sought can come after several others
    if re.search(r'last in a sequence', find_part) is not None:
        sequence = True
        if re.search(r'skipping +\[', abort_part) is not None:
            skips = re.search(r"skipping +(\[.+?])", abort_part).group(1)
        elif re.search(r'skipping +\'', abort_part) is not None:
            skips = re.search(r"skipping +\'(.+?)\'", 
                abort_part).group(1).split()
        if re.search(r'sequence contains +\[', abort_part) is not None:
            seq_abort = re.search(r"sequence contains +(\[.+?])", 
                abort_part).group(1)
        elif re.search(r'sequence contains +\'', abort_part) is not None:
            seq_abort = re.search(r"sequence contains +\'(.+?)\'", 
                abort_part).group(1).split()
    else:
        sequence = False
    for start_word in start_here:
        # Starting point for pattern can be a tag or a word
        if word[word_number].tag == start_word or \
           word[word_number].spelling.lower() == start_word:
            if direction == 'backward':
                begin, end, step = word_number - 1, word_number - length - 1, -1
            else:
                begin, end, step = word_number + phrase_offset + 1, \
                    word_number + phrase_offset + length + 1, 1
            if begin < 0: begin = 0
            if end > wordcount: end = wordcount
            for this in range(begin, end, step):
                # Sequence check; move to the end of the sequence
                # Only left-to-right sequences are currently supported
                if sequence:
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
                # Early stop condition or end-of-sentence check
                if early_stop != 'no stop condition' and \
                    (word[this].tag in early_stop or
                         word[this].spelling.lower() in early_stop or
                         word[this].spelling == '.'):
                    break  # No match; found cancelling stop condition
                # Negative condition check
                if re.search(r' for missing ', find_part) is not None and \
                    (word[this].spelling.lower() in pattern_end or \
                    word[this].tag in pattern_end):
                    break  # No match; negative condition satisfied
                # Condition checks
                if (pattern_end == '_SVS_' and
                    start_word == 'a' and
                    word[this].spelling.lower()[0] in \
                        ['a', 'e', 'i', 'o', 'u']) or \
                        (pattern_end == '_SCS_' and
                        start_word == 'an' and
                        word[this].spelling.lower()[0] in
                        string.ascii_letters and
                        word[this].spelling.lower()[0] not in
                        ['a', 'e', 'i', 'o', 'u', 'h']) or \
                        word[this].tag in pattern_end or \
                        word[this].spelling.lower() in pattern_end:
                    # pattern succesfully matched; print out match
                    print_attribute(attribute_name, this, direction)
                    return True
                # Negative condition check continued
                if re.search(r' for missing ', find_part) is not None:
                    if (direction == 'backward' and this == end + 1) or \
                        this == end - 1:
                        # pattern successfully matched; print out match
                        print_attribute(attribute_name, this, direction)
                        return True
    return False

def adj():
    """ Check for 'many' followed by a singular noun.
        Example: 'I don't have many carrot.'
    """
    global attr
    if check_rule("Attribute: 'many with sing noun'. \
        From 'many' check forward 8 words for ['NN', 'NNP']. \
        But stop looking if tags ['NNS', 'NNPS'] are found first."): \
        attr['adj-many'] = attr['adj-many'] + 1

def adjcmp():
    """ Attributes based on comparative adjectives """
    global attr
    pass

def adjsup():
    """ Attributes based on superlative adjectives """
    global attr
    pass

def adv():
    """ adverb, tag 'RB' 
        Check for 'almost' used like 'most'
        example: 'Almost sea creatures are fish.'
    """
    global attr
    if check_rule("Attribute: 'almost used like most'. \
        From 'almost' check forward 1 word for \
        ['JJ', 'NNS', 'NNPS']. No stop condition. "):
        attr['adv-almost'] = attr['adv-almost'] + 1 
    """ if check_rule("Attribute: 'almost used like most'. 
        From 'almost' check forward 1 word for missing 
        ['all', 'no', 'any', 'CD', 'anyone', 'anybody', 
             'never', 'always', 'JJ', 'DT']. 
        No stop condition."):
        attr['adv-almost'] = attr['adv-almost'] + 1   
    """

def advcmp():
    """ Attributes based on comparative adverbs """
    global attr
    pass

def dtrm():  
    """ Attributes based on determiners 
        such as a, an, the, this, that, each, every, no, all
    """
    # Check for 'a' followed by vowel sound.
    # Example: 'I don't have a eraser.'
    global attr
    if check_rule("Attribute: 'determiner a/an vowel/cons'. \
        From 'a' check forward 1 word for starting vowel sound. \
        But ignore it if \
        ['u', 'unesco', 'united', 'universal', 'utility', 'uniquely', \
        'university', 'uniform'] are found."): \
        attr['dtrm-a'] = attr['dtrm-a'] + 1

    # Check for 'an' followed by consonant sound.
    # Example: 'I saw an big boat.'
    if check_rule("Attribute: 'determiner a/an vowel/cons'. \
        From 'an' check forward 1 word for starting consonant sound. \
        No stop condition."): \
        attr['dtrm-an'] = attr['dtrm-an'] + 1

    # Check for 'both of' followed by nouns.
    # Example: 'I talked with both of Joe and Bob.'
    if check_rule("Attribute: 'determiner both'. \
        From the phrase 'both of' check forward 1 word \
        for ['NN', 'NNS', 'NNP', 'NNPS']. \
        No stop condition."): \
        attr['dtrm-both'] = attr['dtrm-both'] + 1

    # Check for 'a, an, this, or that' followed by plural noun
    # possibly coming after adjectives and noun modifiers.
    # Example: 'She doesn't like a train station dogs.'
    if check_rule("Attribute: 'determiner sing/plur'. \
        From ['a', 'an', 'this'] check forward 1 word \
        but skipping ['VBG', 'JJ'] \
        for the last in a sequence of \
        ['NN', 'NNP', 'NNS', 'NNPS']. \
        But ignore it if the sequence contains \
        ['few', 'means', 'lot', 'using'], \
        or the end is \
        ['NN', 'NNP', 'centers', 'species', 'strikes', 'rhinoceros']. "): \
        attr['dtrm-dsp'] = attr['dtrm-dsp'] + 1

    # TBD: A separate rule like the one above for 'that' which
    # allows for an adjective after that as in 'it isn't that good'

    # Check for 'some' instead of 'any' after a negative verb.
    # Example: 'He doesn't need some salt.'
    if check_rule("Attribute: 'determiner some/any'. \
        From 'some' check backward 6 words for ['not', 't']. \
        No stop condition."): \
        attr['dtrm-some'] = attr['dtrm-some'] + 1

def noun():
    """ Attributes based on nouns. """
    global attr

    # Check for 'reason(s)' used ungrammatically.
    # Example: 'My reason to doing that is I want to.'
    if check_rule("Attribute: 'noun reasons'. \
        From ['reason', 'reasons'] check forward 2 words \
        for missing ['for', 'that', 'why', 'is', 'because']. \
        No stop condition."): \
        attr['noun-reason'] = attr['noun-reason'] + 1

    # Check for 'lot of' followed by singular instead of plural.
    # Example: 'I bought a lot of thing today.'
    if check_rule("Attribute: 'noun sing/plur'. \
        From 'lot' check forward 6 words for 'NN'. \
        But ignore it if ['VBG', 'NNS'] are found."): \
        attr['noun-sp'] = attr['noun-sp'] + 1 

    # Check for singular noun followed by wrong verb type.
    # Example 'He like to bowl.'
    if check_rule("Attribute: 'noun subj-verb disagreement'. \
        From 'NN' check forward 1 word for 'VBP'. \
        No stop condition."): \
        attr['noun-svdis'] = attr['noun-svdis'] + 1

    # check for 'thing' without a determiner
    #  Example: 'I wanted thing to fix the car.'
    if check_rule("Attribute: 'determiner noun'. \
        From ['thing', 'importance'] \
        check backward 3 words for missing ['DT', 'one', 'PRP$']. \
        No stop condition."): \
        attr['dtrm-noun'] = attr['dtrm-noun'] + 1

def prep():
    """ preposition """
    global attr
    pass

def prnper():
    """ personal pronoun """
    global attr
    pass

def prnpos():
    """ possessive pronoun """
    global attr
    pass

def to():
    """ the word 'to', tag 'TO' """
    global attr
    pass

def verb():
    """ Check for 'agree' not followed by 'with', 'to', 'that', or ','.
        Example: I agree this idea.
    """
    global word_number, attr
    if check_rule("Attribute: 'preposition missing'. \
        From 'agree' check forward 2 words for missing \
        ['with', 'to', 'that', ',']. No stop condition."): \
        attr['verb-prp'] = attr['verb-prp'] + 1

    # check for missing verb after 'can'
    #  example: I can many miles.
    if check_rule("Attribute: 'verb missing'. \
        From 'can' check forward 3 words for missing \
        ['VB', 'VBD', 'VBP']. No stop condition."): \
        attr['verb-can'] = ['verb-can'] + 1

def whdtrm():
    """ WH-determiner; can be that, what, whatever, which, whichever """
    global attr
    pass

# Match part of speech code to functions to be run.
tags = {'DT': dtrm, 'IN': prep, 'JJ': adj, 'JJS': adjsup,
        'JJR': adjcmp,
        'NN': noun, 'NNP': noun, 'NNPS': noun, 'NNS': noun,
        'PRP': prnper, 'PRP$': prnpos, 'RB': adv, 'RBR': advcmp,
        'TO': to, 'VB': verb,
        'VBD': verb, 'VBG': verb, 'VBP': verb, 'VBZ': verb,
        'WDT': whdtrm}

# Trigram attribute strings for each part of speech
tgm_tags = {'DT': 'dtrm', 'IN': 'prep', 'JJ': 'adj', 'JJR': 'adjcmp',
            'JJS': 'adjsup', 'NN': 'noun', 'NNP': 'noun',
            'NNPS': 'noun', 'NNS': 'noun',
            'PRP': 'prnper', 'PRP$': 'prnpos', 'RB': 'adv',
            'RBR': 'advcmp', 'TO': 'to', 'VB': 'verb',
            'VBD': 'verb', 'VBG': 'verb', 'VBP': 'verb', 'VBZ': 'verb',
            'WDT': 'whdtrm'}

checkwords = ["of", "in", "to", "for", "with", "on", "at", "by", "from", 
              "into", "about", "a", "an", "the", "this", "that", "these", 
              "those", "my", "your", "his", "her", "its", "our", "their", 
              "both", "each", "either", "enough", "every", "all", "another", 
              "any", "few", "fewer", "less", "little", "many", "more", "most",
              "much", "neither", "no", "other", "several", "some"]

# checkwords = ["from", "all"]

def apply_rules():
    """ For each sentence, for each tagged word in the sentence, do 
        attribute check (function) corresponding to part of speech tag 
        in 'tags' dictionary.
        precondition: trigram_corpus_check has been run """
    global word, word_number, sentence_list
    reportfile.write("Grammar attributes found in the text \
        using handwritten rules:\n\n")
    last_sentence = None
    for item in range(len(word)):
        # run grammatical rules function based on part of speech
        if word[item].tag in tags:
            word_number = word[item].number
            tags[word[item].tag]()

def file_len(fname):
    """ Use shell command 'wc' to quickly get lines in file. """
    file_sizes = {}
    if file_sizes.get(fname, None):
        return file_sizes[fname]
    p = subprocess.Popen(['wc', '-l', fname], \
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    result = int(result.strip().split()[0])
    file_sizes[fname] = result
    return result

def measure(path, documents):
    """ Measure attributes in documents and
        put measurements in 'result_dictionaries' and
        'X' for SVM input. 
    """
    global yahoo_misslist, attr, reportfile
    result_dictionaries = []
    for filename in documents:
        for (k, v) in attr.iteritems():
            attr[k] = 0
        yahoo_misslist = []
        # start report file for this document
        reportfile = open(path + "/report/" + filename + "_rpt", "w")
        reportfile.write("Grammatical analysis report for '%s' file.\n" % 
             (path + "/" + filename))
        tagged_text = tag_file(path, filename)
        trigram_corpus_check(tagged_text)
        apply_rules()
        this_result = sorted(attr.iteritems(), key=itemgetter(0))
        reportfile.write("\nattribute dictionary: \n%s" % this_result)
        reportfile.close()
        result_dictionaries.append(this_result)
    unscaled_X = []
    for row in range(len(result_dictionaries)):
        unscaled_X.append([v for (k, v) in result_dictionaries[row]])
    return unscaled_X

def scale_training_X(unscaled_X):
    """ Convert training result_dictionaries to
        X arrays of attribute measurements for SVMs
        scale X attributes to the range 0 to 1.0.
    """
    global maxes
    maxes = unscaled_X[0]
    for row in range(1, len(unscaled_X)):
        maxes = [max(i, j, 1) for i, j in zip(unscaled_X[row], maxes)]
    print("Maximums (for scaling): \n%s" % maxes)
    # if SVM model is being saved, save scaling factors too
    if args.s:
        joblib.dump(maxes, "scalefactors.pkl")
    X = []
    # apply scaling factors to X
    for row in range(len(unscaled_X)):
        X.append([i / float(j) for i, j in zip(unscaled_X[row], maxes)])
    return X

def scale_test_X(unscaled_X):
    """ Use previously saved scaling if -r option is selected. """
    global maxes
    if args.r:
        if not os.path.exists("scalefactors.pkl"):
            print("Error: use saved SVM model option -r selected, ")
            print("but cannot find scalefactors.pkl")
            sys.exit()
        else:
            maxes = joblib.load("scalefactors.pkl")
    X = []
    for row in range(len(unscaled_X)):
        X.append([i / float(j) for i, j in zip(unscaled_X[row], maxes)])
    return X

def listfiles(filepath):
    """ List files in subdirectory omitting dotfiles, backups, 
        and sub-subdirectories. 
    """
    files = []
    for (dirpaths, dirnames, filenames) in os.walk(filepath):
        files.extend(filenames)
        break  # don't get subdirectory filenames
    # remove hidden files and automatic backup files
    changed = True
    while changed:
        changed = False
        for name in files:
            if (name[0] == ".") or ('~' in name):
                files.remove(name)
                changed = True
    return sorted(files)

# Directory setup
# Get paths for subdirectories from command line if provided
parser = argparse.ArgumentParser(description='Identify and classify \
    errors in English text') 
parser.add_argument('-l', action='store_true', 
    help='use linear kernel instead of default RBF kernel')
parser.add_argument('-y', action='store_true', 
    help='use yahoo online instead of saved yahoo data')
parser.add_argument('-s', action='store_true', 
    help='save SVM model to model.pkl file after training')
parser.add_argument('-r', action='store_true', 
    help="don't train; use saved SVM model for classifier")
parser.add_argument('-e', 
    help='specify subdirectory for training documents with errors')
parser.add_argument('-ne', 
    help='specify subdirectory for training documents without errors')
parser.add_argument('-te',
    help='specify subdirectory for test documents with \
    errors or documents to be classified with errors unknown')
parser.add_argument('-tne', 
    help='specify subdirectory for test documents without errors')

args = parser.parse_args()
# Create default directories
if not args.e:
    args.e = 'training-docs-with-errors'
if not args.ne:
    args.ne = 'training-docs-no-errors'
if not args.te:
    args.te = 'test-docs-with-errors'
if not args.tne:
    args.tne = 'test-docs-no-errors'
# Make specified subdirectories if necessary
if not args.r:
    if not os.path.exists(args.e):
        print("making %s subdirectory\n" % args.e)
        os.mkdir(os.getcwd() + "/" + args.e)
    if not os.path.exists(args.ne):
        print("making %s subdirectory\n" % args.ne)
        os.mkdir(os.getcwd() + "/" + args.ne)
if not os.path.exists(args.te):
    print("making %s subdirectory\n" % args.te)
    os.mkdir(os.getcwd() + "/" + args.te)
if not os.path.exists(args.tne):
    print("making %s subdirectory\n" % args.tne)
    os.mkdir(os.getcwd() + "/" + args.tne)
# Make report and tag subdirectories if necessary  
if not args.r:
    if not os.path.exists(args.e + "/report"):
        os.mkdir(args.e + "/report")
    if not os.path.exists(args.ne + "/report"):
        os.mkdir(args.ne + "/report")
if not os.path.exists(args.te + "/report"):
    os.mkdir(args.te + "/report")
if not os.path.exists(args.tne + "/report"):
    os.mkdir(args.tne + "/report")
if not os.path.exists(args.e + "/tag"):
    os.mkdir(args.e + "/tag")
if not os.path.exists(args.ne + "/tag"):
    os.mkdir(args.ne + "/tag")
if not os.path.exists(args.te + "/tag"):
    os.mkdir(args.te + "/tag")
if not os.path.exists(args.tne + "/tag"):
    os.mkdir(args.tne + "/tag")
results_file = open("classifier-output", "w")

word_number = 0
wordcount = 0
sentence_list = []
yahoo_misslist = []
yahoo_discarded = []
word = []
maxes = []
numpy.set_printoptions(precision=2)
# Names of attributes; used to separate types.
# For example, 'dtrm' is part of all determiner attributes
attr = dict.fromkeys(
    ['adj-many', 'adj-tgm', 'adjcmp-tgm', 'adjsup-tgm',
     'adv-almost', 'adv-tgm', 'advcmp-tgm',
     'dtrm-a', 'dtrm-an', 'dtrm-both', 'dtrm-dsp',
     'dtrm-noun', 'dtrm-some', 'dtrm-tgm',
     'noun-reason', 'noun-sp', 'noun-svdis', 'noun-tgm',
     'prep-tgm', 'prnper-tgm', 'prnpos-tgm', 'to-tgm',
     'verb-can', 'verb-prp', 'verb-tgm',
     'whdtrm-tgm'], 0)
# get columns for determiner SVM
all_col_nums = range(0, len(attr))
for n, k in enumerate(sorted(attr)):
    attr[k] = all_col_nums[n]
dtrm_attr = dict()
for k, v in attr.iteritems():
    if 'dtrm' in k:
        dtrm_attr[k] = v
dtrm_columns = sorted(dtrm_attr.values())
print("Features for determiner SVM: %s" % dtrm_columns)

if args.r:
    # Load previously saved SVM model instead of training
    model = libsvm.svmutil.svm_load_model('svm_model')
else:
    # Train SVM as usual
    if len(os.listdir(args.e)) < 3:
        print("Please place documents in the %s directory" % args.e)
        print("and enter 'c' to continue, or enter anything else to exit.")
        answer = input()
        if answer != 'c':
            sys.exit()
    if len(os.listdir(args.ne)) < 3:
        print("Please place documents in the %s directory" % args.ne)
        print("and enter 'c' to continue, or enter anything else to exit.")
        answer = input()
        if answer != 'c':
            sys.exit()
    bad_docs = listfiles(args.e)
    bad_doc_qty = len(bad_docs)
    error_X = measure(args.e, bad_docs)
    good_docs = listfiles(args.ne)
    good_doc_qty = len(good_docs)
    no_error_X = measure(args.ne, good_docs)
    training_docs = bad_docs + good_docs
    print("Tagging and measuring features in training documents")
    unscaled_X = error_X + no_error_X
    X = scale_training_X(unscaled_X)

    # Extract array X for dtrm SVM having only dtrm attributes
    dtrm_X = (numpy.array(X)[:, dtrm_columns]).tolist()
    unscaled_dtrm_X = (numpy.array(unscaled_X)[:, dtrm_columns]).tolist()
    results_file.write("Training document feature measurements\n")
    results_file.write("Document \
         Unscaled dtrm features     Scaled dtrm features\n")
    for r, row in enumerate(dtrm_X):
        results_file.write(
            "%s  %s  [%s]\n" % (training_docs[r], 
            unscaled_dtrm_X[r], ', '.join('%.2g' % item for item in row)))
    # Make label array for training, bad docs first
    dtrm_Y = ([1] * bad_doc_qty) + ([0] * good_doc_qty)
    results_file.write("Training labels \
        (1 indicates grammatical error): \n %s\n" % dtrm_Y)
    # Train dtrm SVM
    prob = libsvm.svm_problem(dtrm_Y, dtrm_X)
    param = libsvm.svm_parameter()
    if args.l:
        param.kernel_type = "LINEAR"
    # The code below causes an error due to a libsvm bug,
    #   but RBF is default anyway
    # else:
    # param.kernel_type = RBF
    model = libsvm.svmutil.svm_train(prob, param)
    if args.s:
        print("Saving the trained SVM model to 'svm_model'\n")
        libsvm.svmutil.svm_save_model("svm_model", model)

# Measure attributes in test documents
if len(os.listdir(args.te)) < 3:
    print("Please place documents in the %s directory" % args.te)
    print("and enter 'c' to continue, or enter anything else to exit.")
    answer = input()
    if answer != 'c':
        sys.exit()
if len(os.listdir(args.tne)) < 3:
    print("Please place documents in the %s directory" % args.tne)
    print("and enter 'c' to continue, or enter anything else to exit.")
    answer = input()
    if answer != 'c':
        sys.exit()
test_docs_errors = listfiles(args.te)
unscaled_error_test_X = measure(args.te, test_docs_errors)
test_docs_clean = listfiles(args.tne)
unscaled_no_error_test_X = measure(args.tne, test_docs_clean)
test_docs = test_docs_errors + test_docs_clean
test_doc_qty = len(test_docs)
print("Tagging and measuring features in documents to be classified")
unscaled_test_X = unscaled_error_test_X + unscaled_no_error_test_X
print("unscaled_test_X looks like this:")
print(unscaled_test_X)
test_X = scale_test_X(unscaled_test_X)
print("test_X looks like this:")
print(test_X)
results_file.write("Dtrm columns: %s\n" % dtrm_columns)
unscaled_dtrm_test_X = \
    (numpy.array(unscaled_test_X)[:, dtrm_columns]).tolist()
dtrm_test_X = (numpy.array(test_X)[:, dtrm_columns]).tolist()
results_file.write("Test document feature measurements\n")
results_file.write("Document Unscaled dtrm test features \
                    Scaled dtrm test features\n")
for r, row in enumerate(dtrm_test_X):
    results_file.write(
        "  %s    %s      [%s]\n" % (test_docs[r], unscaled_dtrm_test_X[r], ', \
        '.join('%.2g' % item for item in row)))

# Classify with SVM
test_results = libsvm.svmutil.svm_predict([0] * len(dtrm_test_X), 
    dtrm_test_X, model)
print("Test results from SVM: \n%s" % (test_results[0]))
results_file.write("Test results from SVM: \n%s\n" % test_results[0])
dtrm_error_sums = []
for test in dtrm_test_X:
    dtrm_error_sums.append(sum(test))
testdocinfo = [[0 for col in range(5)] 
               for row in range(len(test_docs))]
for row, doc in enumerate(test_docs_errors):
    testdocinfo[row][0] = test_docs[row]
    testdocinfo[row][1] = 'errors'
    if test_results[0][row] > 0:
        testdocinfo[row][2] = 'errors'
    else:
        testdocinfo[row][2] = 'clean'
    testdocinfo[row][3] = dtrm_error_sums[row]
offset = len(test_docs_errors)
for row, doc in enumerate(test_docs_clean):
    row2 = row + offset
    testdocinfo[row2][0] = test_docs[row2]
    testdocinfo[row2][1] = 'clean'
    if test_results[0][row2] > 0:
        testdocinfo[row2][2] = 'errors'
    else:
        testdocinfo[row2][2] = 'clean'
    testdocinfo[row2][3] = dtrm_error_sums[row + offset]
print("\n        filename  truth  SVM class     attributes\n")
for row in testdocinfo:
    print(' %12s %9s %9s        %3.1f' % (row[0], row[1], row[2], row[3]))
results_file.write("       filename    truth   \
    SVM class         attributes\n")
for row in testdocinfo:
    results_file.write("%14s %9s  %9s              %3.1f\n" % 
    (row[0], row[1], row[2], row[3]))
results_file.close()

# Ideas for future development:
# Add attributes for more types of grammatical errors
# Use an SVM in a separate process for each type of error
# Make a pie chart graphic showing proportions of types of errors
