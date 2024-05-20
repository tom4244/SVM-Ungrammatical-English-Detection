#!/usr/bin/perl
# script to prepare Google 5gram corpus for use with Stanford Parser
# including deleting non-5gram lines, combining lines with identical
# ngrams from different years (adding quantities),
# and converting contents such as contractions to Stanford Parser formats
use strict;
use warnings;

my @files = grep { -f } glob( '*.csv' );
print "filtering and combining lines and adding quantities\n";
while (<@files>) {
  print "processing " . $_ . ".\n";    
  open (CSVFILE, "<", $_) or die "couldn't open infile: $!";
  my $outfile = $_;
  $outfile =~ s/.*-(\d+)\.csv/corpus$1/;
  # using perl grep below was much slower than using the while loop
  my $lastgram = "";
  my $lasttimes = 0;
  my @totaled_lines;
  while (<CSVFILE>) {
    if (/\S+\s\S+\s\S+\s\S+\s\S+\t\d+\t\d+\t\d+\t\d+/) {
      (my $ngram, my $year, my $times) =
          (/(\S+\s\S+\s\S+\s\S+\s\S+)\t(\d+)\t(\d+)\t\d+\t\d+/); 
      if ($ngram eq $lastgram) {
        $times += $lasttimes;
        pop (@totaled_lines);    
      }
      $lastgram = $ngram;
      $lasttimes = $times;
      my $outline = $ngram . " " . $year . " " . $times . "\n";
      push (@totaled_lines, $outline);        
    }    
  }
  close (CSVFILE) or die "can't close input file: $!";
  # clean up contractions, extraneous quotes, etc.
  #  for ex. "we ' ve" to match Stanford Parser style "we 've"
  #  and " to Stanford '' and 'word"' to 'word'
  open (OUTFILE, "+>", $outfile) or die "couldn't open outfile: $!";  
  foreach my $line (@totaled_lines) {
      $_ = $line;     
      s/"+/"/g;
      s/(\S)"/$1/g;
      s/"!/!/g;
      s/\"/\'\'/g;
      s/(\S{2,})'(\S+)/$1 ' $2/g;
      s/n ' (t\s+)/ n'$1/g;    
      s/(^| )' (m\s+)/ '$2/g;
      s/(^| )' (d\s+)/ '$2/g;
      s/(^| )' (s\s+)/ '$2/g;
      s/(^| )' (t\s+)/ '$2/g;
      s/(^| )' (ve\s+)/ '$2/g;
      s/(^| )' (re\s+)/ '$2/g;
      s/(^| )' (ll\s+)/ '$2/g;    
      s/ '\t/\t/;
      s/(^| )''(.) /$1'' $2 /g;
      print OUTFILE $_;      
  }
  #my @foo2 = grep(/( of | in | to | for | with | on | at | by | from | into | about | through )/, @foo);
  close (OUTFILE) or die "can't close output file: $!";
}

