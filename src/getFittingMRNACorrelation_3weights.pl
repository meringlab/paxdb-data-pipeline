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

my $file = shift @ARGV; #"/Users/gabriele/testBASH/3weightFiles_sharedProteins_withMRNA_for3files_SchizosaccharomycesPombe_fissionYeast.txt";

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
my $nrProtsIDS=$fileArray[7]; $nrProtsIDS=~ /\[1\] number proteins of integrated dataset:  (.+)$/; my $nrProts=$1;
# total number mRNA
my $nrProtsMRNA=$fileArray[9]; $nrProtsMRNA=~ /\[1\] total number of mRNA:  (.+)$/; my $nrMRNA=$1;
# shared mRNA proteins
my $sharedProtsWithMRNA=$fileArray[14]; $sharedProtsWithMRNA=~ /\[1\] shared mRNA proteins:  (.+)$/; my $sharedProts=$1; 

print "headline____".$nrProts."__".$nrMRNA."__".$sharedProts."\n";


my $line1=3; 	# weight1
my $line2=4; 	# weight2
my $line3=5; 	# weight3
my $line4=13;	# correlation	
for (1..$countWeightedFiles) {
		
	my $wantedWeight1=$fileArray[$line1]; $wantedWeight1=~ /^\[1\]\s(\d\.?\d?).*/; my $weight1=$1;
	my $wantedWeight2=$fileArray[$line2]; $wantedWeight2=~ /^\[1\]\s(\d\.?\d?).*/; my $weight2=$1;
	my $wantedWeight3=$fileArray[$line3]; $wantedWeight3=~ /^\[1\]\s(\d\.?\d?).*/; my $weight3=$1;
	
	my $correlationMRNA=$fileArray[$line4]; $correlationMRNA=~ /\[1\] correlation: (.+)$/; my $correlation=$1; 
		
	print $weight1."_".$weight2."_".$weight3."____".$correlation."\n";
	
	$line1+=16;
	$line2+=16;
	$line3+=16;
	$line4+=16;
}










#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 SchizosaccharomycesPombe_FissionYeast_PRIDE.SC
#4 [1] 1 Spombe_Alex_2012_09_experiment
#5 [1] 1 Spombe_Alex_2012_09_spectral_count
#6 [1] 
#7 [1] number proteins of integrated dataset:  916
#8 [1] 
#9 [1] total number of mRNA:  2126
#10 [1] 
#11 [1] CORRELATION
#12 [1] mRNA  -  integratedDataset
#13 [1] correlation: 0.543
#14 [1] shared mRNA proteins:  418                   
#15 [1] 

#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 SchizosaccharomycesPombe_FissionYeast_PRIDE.SC
#4 [1] 1 Spombe_Alex_2012_09_experiment
#5 [1] 0.1 Spombe_Alex_2012_09_spectral_count
#6 [1] 
#7 [1] number proteins of integrated dataset:  916
#8 [1] 
#9 [1] total number of mRNA:  2126
#10 [1] 
#11[1] CORRELATION
#12 [1] mRNA  -  integratedDataset
#13 [1] correlation: 0.528
#14 [1] shared mRNA proteins:  418                   
#15 [1] 












		


















		