#!/usr/bin/perl -w
#Truncate the Bing word frequency list (to be used in the
#  trigram checker) to 5000 items and add a frequency
#  ranking number to each word)
use warnings;
use strict;
use autodie;

my $thisfile = glob("../corpuses/Bing*/Bing100k.txt");
open my $oldcorpus, '<', $thisfile;
open my $newcorpus, ">", $thisfile . ".sorted5000";

my $linenumber = 0;
my @wordlist = ();
while (<$oldcorpus>) {
   chomp();
   s/(\S+)/$1 $linenumber/;   
   push(@wordlist, $_);
   $linenumber += 1;
   last if $linenumber == 5000;
}
@wordlist = sort(@wordlist);
for (my $i = 0; $i < 10; $i++) {
    print $wordlist[$i] . "\n";
}
$linenumber = 0;
my $longest = 0;
my $linelen = 0;
foreach my $line (@wordlist) {
    #chomp();
    $linelen = length($line);
    if ($linelen > $longest) {
        $longest = $linelen;
    }
    print $newcorpus $line . "\n";
    $linenumber += 1;
    last if ($linenumber > 4999);       
}
print "the longest was ", $longest, "\n";
close $oldcorpus;
close $newcorpus;

