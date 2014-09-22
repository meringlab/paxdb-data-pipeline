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
my $nrProtsIDS=$fileArray[13]; $nrProtsIDS=~ /\[1\] number proteins of integrated dataset:  (.+)$/; my $nrProts=$1;
# total number mRNA
my $nrProtsMRNA=$fileArray[15]; $nrProtsMRNA=~ /\[1\] total number of mRNA:  (.+)$/; my $nrMRNA=$1;
# shared mRNA proteins
my $sharedProtsWithMRNA=$fileArray[20]; $sharedProtsWithMRNA=~ /\[1\] shared mRNA proteins:  (.+)$/; my $sharedProts=$1; 

print "headline____".$nrProts."__".$nrMRNA."__".$sharedProts."\n";


my $line0=19;	# correlation
my $line1=3; 	# weight1
my $line2=4; 	# weight2
my $line3=5; 	# weight3
my $line4=6; 	# weight4
my $line5=7; 	# weight5
my $line6=8; 	# weight6
my $line7=9; 	# weight7
my $line8=10; 	# weight8
my $line9=11; 	# weight9
	
for (1..$countWeightedFiles) {
		
	my $wantedWeight1=$fileArray[$line1]; $wantedWeight1=~ /^\[1\]\s(\d\.?\d?).*/; my $weight1=$1;
	my $wantedWeight2=$fileArray[$line2]; $wantedWeight2=~ /^\[1\]\s(\d\.?\d?).*/; my $weight2=$1;
	my $wantedWeight3=$fileArray[$line3]; $wantedWeight3=~ /^\[1\]\s(\d\.?\d?).*/; my $weight3=$1;
	my $wantedWeight4=$fileArray[$line4]; $wantedWeight4=~ /^\[1\]\s(\d\.?\d?).*/; my $weight4=$1;
	my $wantedWeight5=$fileArray[$line5]; $wantedWeight5=~ /^\[1\]\s(\d\.?\d?).*/; my $weight5=$1;
	my $wantedWeight6=$fileArray[$line6]; $wantedWeight6=~ /^\[1\]\s(\d\.?\d?).*/; my $weight6=$1;
	my $wantedWeight7=$fileArray[$line7]; $wantedWeight7=~ /^\[1\]\s(\d\.?\d?).*/; my $weight7=$1;
	my $wantedWeight8=$fileArray[$line8]; $wantedWeight8=~ /^\[1\]\s(\d\.?\d?).*/; my $weight8=$1;
	my $wantedWeight9=$fileArray[$line9]; $wantedWeight9=~ /^\[1\]\s(\d\.?\d?).*/; my $weight9=$1;
	
	my $correlationMRNA=$fileArray[$line0]; $correlationMRNA=~ /\[1\] correlation: (.+)$/; my $correlation=$1; 
		
	print $weight1."_".$weight2."_".$weight3."_".$weight4."_".$weight5."_".$weight6."_".$weight7."_".$weight8."_".$weight9."____".$correlation."\n";
	
	$line0+=22;	
	$line1+=22;
	$line2+=22;
	$line3+=22;
	$line4+=22;
	$line5+=22;
	$line6+=22;
	$line7+=22; 	
	$line8+=22; 
	$line9+=22; 
}






#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 SE_BuildMay2009
#4 [1] 1 BuildApril09
#5 [1] 0.7 GPM_2012_09_Saccharomyces_cerevisiae.SC
#6 [1] 0.7 DeGodoy_et_al_yeast_data
#7 [1] 0.5 Newman_et_al_yeast_data_YEPD
#8 [1] 0.5 Newman_et_al_yeast_data_SD
#9 [1] 0.8 SE_Yeast_Lu_2007_YMD
#10 [1] 0.8 SE_Yeast_Lu_2007_YPD
#11 [1] 0.1 Ghaemmaghami_et_al_yeast_data
#12 [1] 
#13 [1] number proteins of integrated dataset:  6159
#14 [1] 
#15 [1] total number of mRNA:  5197
#16 [1] 
#17 [1] CORRELATION
#18 [1] mRNA  -  integratedDataset
#19 [1] correlation: 0.641
#20 [1] shared mRNA proteins:  5061                  
#21 [1] 

#0 [1] ################# NEW FILE ########################
#1 [1] 
#2 [1] weights of files: 
#3 [1] 1 SE_BuildMay2009
#4 [1] 1 BuildApril09
#5 [1] 0.9 GPM_2012_09_Saccharomyces_cerevisiae.SC
#6 [1] 0.9 DeGodoy_et_al_yeast_data
#7 [1] 0.4 Newman_et_al_yeast_data_YEPD
#8 [1] 0.4 Newman_et_al_yeast_data_SD
#9 [1] 0.4 SE_Yeast_Lu_2007_YMD
#10 [1] 0.4 SE_Yeast_Lu_2007_YPD
#11 [1] 0.1 Ghaemmaghami_et_al_yeast_data
#12 [1] 
#13 [1] number proteins of integrated dataset:  6159
#14 [1] 
#15 [1] total number of mRNA:  5197
#16 [1] 
#17 [1] CORRELATION
#18 [1] mRNA  -  integratedDataset
#19 [1] correlation: 0.643
#20 [1] shared mRNA proteins:  5061                  
#21 [1] 















		