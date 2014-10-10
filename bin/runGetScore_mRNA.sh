#!/bin/bash
cd /home/gabi/PaxDb/


myMRNAfile=$1
mytmpFileName=$2 
outputfile=$3 
getFittingMRNA=$4
path=$5
namesOfFiles=($6)



#IFS=$'\n'  #IFS == special variable (Internal Field Separator)
fileArray=$(ls /local/eris/gabi/PaxDb/tmp/ | grep "^$mytmpFileName.*txt-1")
#fileArray2=$(ls /local/eris/gabi/PaxDb/tmp/ | grep '^all_dehubbing_4932_SaccharomycesCerevisiae_yeast-integrData_weighted_.*txt-1')

#for i in ${fileArray[@]}; do echo $i; done
#exit


#get mRNA correlations from file
arry=$(/usr/bin/perl -w $getFittingMRNA $myMRNAfile) 


read -r -d '' -a weightsFromFile <<< "$arry"
#get generally information (nr protein of integrated dataset and mRNA data, nr shared proteins)
generallyInformation=${weightsFromFile[0]/*___/}
unset weightsFromFile[0]
#echo $generallyInformation
numbers=${generallyInformation%__*}
nrProteins=${numbers/__*/}
totalNrProteinsMRNA=${numbers/*__/}
sharedProteinsWithMRNA=${generallyInformation#*__*__}



#header of outputfile
echo -n '# '  >> $outputfile  #-n == no newline
date +"%Y-%m-%d" >> $outputfile
for ds in ${namesOfFiles[*]}; do echo '# '$ds; done >> $outputfile
echo "# nr proteins of integrated file: $nrProteins" >> $outputfile
echo "# total number of mRNA file: $totalNrProteinsMRNA" >> $outputfile
echo "# nr shared proteins (integrated / mRNA ): $sharedProteinsWithMRNA" >> $outputfile
echo "# " >> $outputfile
echo -e "# file name\tscore 1\tscore 2\tscore 3\taverage\tmRNA correlation" >> $outputfile
echo '# delta' >> $outputfile	


for k in $fileArray; do
	file=${k/#$path}
#	echo 'file '$file
	name=${k/-[123]/}
	outputname=${name/.txt/}
#	echo 'outputname '$outputname
	cutOutWeights=${outputname#$mytmpFileName}
#	echo $cutOutWeights; break;
	echo -e -n $outputname'\t' >> $outputfile #print filename
	array[0]=$outputname
	
	for i in {1..3}; do
		
		variable=$( cat $path$name-$i );
		array[$i]=$variable
#		echo 'variable '$variable
		rm -f $path$name-$i;
		
	done

	#print scores tab separated
	for n in ${array[@]:1:3}; do echo $n; done | sort -r -n | while read n; do echo -n -e "$n\t"; done >> $outputfile

	#print average
	for p in ${array[@]:1:3}; do echo $p ; done | awk '{sum+=$1} END { printf "%f",sum/3}' >> $outputfile
	
	
	#get mRNA correaltion 
	for x in ${weightsFromFile[@]}; do
		key=${x/___*/}
		value=${x/*___/}
		if [ $cutOutWeights == $key ]; then
			echo -e "\t$value" >> $outputfile
		fi
		
	done

done

