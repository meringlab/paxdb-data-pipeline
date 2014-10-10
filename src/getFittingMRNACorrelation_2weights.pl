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
my $nrProtsIDS=$fileArray[6]; $nrProtsIDS=~ /\[1\] number proteins of integrated dataset:  (.+)$/; my $nrProts=$1;
# total number mRNA
my $nrProtsMRNA=$fileArray[8]; $nrProtsMRNA=~ /\[1\] total number of mRNA:  (.+)$/; my $nrMRNA=$1;
# shared mRNA proteins
my $sharedProtsWithMRNA=$fileArray[13]; $sharedProtsWithMRNA=~ /\[1\] shared mRNA proteins:  (.+)$/; my $sharedProts=$1; 

print "headline____".$nrProts."__".$nrMRNA."__".$sharedProts."\n";

my $line0=12;	# correlation
my $line1=3; 	# weight1
my $line2=4; 	# weight2
	
for (1..$countWeightedFiles) {
		
	my $wantedWeight1=$fileArray[$line1]; $wantedWeight1=~ /^\[1\]\s(\d\.?\d?).*/; my $weight1=$1;
	my $wantedWeight2=$fileArray[$line2]; $wantedWeight2=~ /^\[1\]\s(\d\.?\d?).*/; my $weight2=$1;
	
	my $correlationMRNA=$fileArray[$line0]; $correlationMRNA=~ /\[1\] correlation: (.+)$/; my $correlation=$1; 
		
	print $weight1."_".$weight2."____".$correlation."\n";
	
	$line0+=15;
	$line1+=15;
	$line2+=15;
}


#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 pombe_cell2012_protein
#4 [1] 1 SchizosaccharomycesPombe_FissionYeast_PRIDE.SC
#5 [1] 
#6 [1] number proteins of integrated dataset:  3616
#7 [1] 
#8 [1] total number of mRNA:  4837
#9 [1] 
#10 [1] CORRELATION
#11 [1] mRNA  -  integratedDataset
#12 [1] correlation: 0.696
#13 [1] shared mRNA proteins:  3548                  
#14 [1] 

#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 pombe_cell2012_protein
#4 [1] 0.5 SchizosaccharomycesPombe_FissionYeast_PRIDE.SC
#5 [1] 
#6 [1] number proteins of integrated dataset:  3616
#7 [1] 
#8 [1] total number of mRNA:  4837
#9 [1] 
#10 [1] CORRELATION
#11 [1] mRNA  -  integratedDataset
#12 [1] correlation: 0.696
#13 [1] shared mRNA proteins:  3548                  
#14 [1] 



