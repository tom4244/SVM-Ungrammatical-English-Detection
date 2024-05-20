#!/usr/bin/perl
# combines lines with identical trigrams, adds quantities, uses latest year
use strict;
use warnings;

print "combining lines and adding quantities\n";
open my $trigrams, "<", 'trigrams' or die "couldn't open infile: $!";
open my $combined, ">", 'trigrams-c' or die "couldn't open outfile: $!";
my $lastgram = "";
my $lastyear = 0;
my $lasttimes = 0;
my $ngram = "";
my $year = 0;
my $times = 0;
while (<$trigrams>) {
  chomp();
  if (/\(\S+\s\S+\)\(\S+\s\S+\)\(\S+\s\S+\)\s\d+\s\d+/) {
    ($ngram, $year, $times) =
        (/(\(\S+\s\S+\)\(\S+\s\S+\)\(\S+\s\S+\))\s(\d+)\s(\d+)/);
    if ($ngram eq $lastgram) {
      $lastyear = $year;
      $lasttimes += $times;
    } else {
      my $outline = $lastgram . " " . $lastyear . " " . $lasttimes . "\n";
      if ($lastgram ne "") {
        print $combined $outline;
      }
      $lastgram = $ngram;
      $lastyear = $year;
      $lasttimes = $times;
    }
  }    
}
close $trigrams or die "can't close input file: $!";
close $combined or die "can't close output file: $!";


