#!/usr/bin/perl
use warnings;
use strict;
use autodie;
# extract individual trigram corpuses for some of the more problematic
# words such as prepositions, determiners, articles
# with the word in question being second word in the trigrams
# pad the file lines with "pad-with-spaces.pl" afterward to 
#  prepare them for binary search

my @words = ("of", "in", "to", "for", "with", "on", "at", "by", "from", "into", "about", "a", "an", "the", "this", "that", "these", "those", "my", "your", "his", "hers", "its", "our", "their", "both", "each", "either", "enough", "every", "all", "another", "any", "few", "fewer", "less", "little", "many", "more", "most", "much", "neither", "no", "other", "several", "some");
#my @words = ("a");

foreach my $word (@words) {
   print $word . "\n";   
   my $detfile = $word . "_corpus";
   open my $whole_thing, '<', "../trigrams";
   open (my $posfile, '>', $detfile);
   while (<$whole_thing>) {
      #if (/^(\([^ ]+? [^ ]+?\)){2}\($word /) {   #5gram version
      if (/^\([^ ]+? [^ ]+?\)\($word /) {   
         print $posfile $_;
      }
   }    
   close $posfile;
   close $whole_thing;
}


