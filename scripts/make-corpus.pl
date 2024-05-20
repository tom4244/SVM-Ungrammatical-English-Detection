#!/usr/bin/perl -w
# make a word corpus out of files containing trigrams
# pull words out of tags and words, sort them, and remove duplicates
use warnings;
use strict;
use utf8::all;
use Encode;

my @files = grep { -f } glob( '*_corpus' );
while (<@files>) {
#open my $infile, '<', $ARGV[0] or die "couldn't open infile: $!";
   open my $infile, '<', $_ or die "couldn't open infile: $!";
#  open my $outfile, ">", $ARGV[0] . ".words" or die "couldn't open outfile: $!";
   open my $outfile, ">", $_ . ".words" or die "couldn't open outfile: $!";
   my @words;
   while (<$infile>) {
      chomp();
      s/ \d+ \d+.*//; # remove unneeded year and quantity numbers
      #take words out of tagged words
      /\((\S+) \S+\)\((\S+) \S+\)\((\S+) \S+\)/;
      push(@words, $1);
      push(@words, $2);
      push(@words, $3);
   }
   #my (@sorted) = <$words>;
   my @sorted = sort @words;
   my $lastword = "";
   foreach my $word (@sorted) {
       #print $word;
       if ($word ne $lastword) {
           #print $word . "\n";
           print $outfile $word . "\n";
       $lastword = $word;
       }
   }
   print $outfile "\n";
   #   binmode $outfile, ":utf8";
   #   print $outfile $_;    

   close $infile or die "can't close input file: $!";
   close $outfile or die "can't close output file: $!";
}
