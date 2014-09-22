#!/usr/bin/perl -w
##################################################################################################
#
#
#
##################################################################################################

use strict;
use warnings;


##################################################################################################
#					Variables						 #
##################################################################################################

my $file = shift @ARGV; #"/Users/gabriele/testBASH/2weightFiles_allProteins_withMRNA_for3files_SchizosaccharomycesPombe_fissionYeast.txt";

##################################################################################################
#					Main Program					 #
##################################################################################################



open (FILE, $file) or die "couldn't open file $file"; 
my @fileArray=<FILE>; #read file into an array
close FILE;



my $countWeightedFiles=0;
foreach my $line (@fileArray) {
	chomp $line;
	if ($line=~ /## NEW FILE ##/) { $countWeightedFiles++; }
}



#these numbers are the same for all integrated datasets
# number proteins of integrated ds
my $nrProtsIDS=$fileArray[10]; $nrProtsIDS=~ /\[1\] number proteins of integrated dataset:  (.+)$/; my $nrProts=$1;
# total number mRNA
my $nrProtsMRNA=$fileArray[12]; $nrProtsMRNA=~ /\[1\] total number of mRNA:  (.+)$/; my $nrMRNA=$1;
# shared mRNA proteins
my $sharedProtsWithMRNA=$fileArray[17]; $sharedProtsWithMRNA=~ /\[1\] shared mRNA proteins:  (.+)$/; my $sharedProts=$1; 

print "headline____".$nrProts."__".$nrMRNA."__".$sharedProts."\n";


my $line0=16;	# correlation
my $line1=3; 	# weight1
my $line2=4; 	# weight2
my $line3=5; 	# weight3
my $line4=6; 	# weight4
my $line5=7; 	# weight5
my $line6=8; 	# weight6
	
for (1..$countWeightedFiles) {
		
	my $wantedWeight1=$fileArray[$line1]; $wantedWeight1=~ /^\[1\]\s(\d\.?\d?).*/; my $weight1=$1;
	my $wantedWeight2=$fileArray[$line2]; $wantedWeight2=~ /^\[1\]\s(\d\.?\d?).*/; my $weight2=$1;
	my $wantedWeight3=$fileArray[$line3]; $wantedWeight3=~ /^\[1\]\s(\d\.?\d?).*/; my $weight3=$1;
	my $wantedWeight4=$fileArray[$line4]; $wantedWeight4=~ /^\[1\]\s(\d\.?\d?).*/; my $weight4=$1;
	my $wantedWeight5=$fileArray[$line5]; $wantedWeight5=~ /^\[1\]\s(\d\.?\d?).*/; my $weight5=$1;
	my $wantedWeight6=$fileArray[$line6]; $wantedWeight6=~ /^\[1\]\s(\d\.?\d?).*/; my $weight6=$1;
	
	my $correlationMRNA=$fileArray[$line0]; $correlationMRNA=~ /\[1\] correlation: (.+)$/; my $correlation=$1; 
		
	print $weight1."_".$weight2."_".$weight3."_".$weight4."_".$weight5."_".$weight6."____".$correlation."\n";
	
	$line0+=19;	
	$line1+=19;
	$line2+=19;
	$line3+=19;
	$line4+=19;
	$line5+=19;
	$line6+=19;
}





















		