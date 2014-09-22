#!/bin/bash
#
#$1 == abundance file
#$2 == interaction file
#
# Originally written by Gabi
#

pathIN="species/"
pathOUT="outputfiles/"
mkdir -p $pathOUT

#echo $1
outputfile=${1/$pathIN/zscores_}
#echo $outputfile
outofile=${outputfile//\//_}
outfile=$pathOUT$outofile
echo $outfile


for i in {1..3}; do

	variable=$(/usr/bin/perl -w bin/PaxDbScore_delta.pl $1 $2) #abundance file #interaction file
#	push variable to array
	array[$i]=$variable
	echo ${array[$i]}  #output on terminal
done



echo -n '# '  >> $outfile # no newline
date +"%Y-%m-%d">> $outfile
echo -n '# '  >> $outfile
echo 'delta' >> $outfile
dataset=${1//*\//}
echo -n '# '  >> $outfile
echo $dataset >> $outfile

for l in ${array[@]}; do
	echo $l 
done | sort >> $outfile


#####         #####
#####dehubbing#####
#####         #####
#echo DEHUBBING
#
#
#for k in {1..3}; do
#
#	variable=$(/usr/bin/perl -w PaxDbScore_delta_dehubbing.pl $1 $2) #abundance file #interaction file
##	push variable to array
#	array_dehub[$k]=$variable #'\n'
#	echo ${array_dehub[$k]}  #output on terminal
#done
#
#
#cd /home/gabi/PaxDb/outputfiles/
#
#
#echo -n '# '  >> $outfile # no newline
#echo 'dehubbing' >> $outfile
#
#echo ${array_dehub[1]} >> $outfile 
#echo ${array_dehub[2]} >> $outfile
#echo ${array_dehub[3]} >> $outfile
#
#for m in ${array_dehub[@]}; do
#	echo $m 
#done | sort >> $outfile





