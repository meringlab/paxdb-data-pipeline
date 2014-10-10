#!/bin/bash

namesOfFiles[0]='ecoli2_resolutionCombination_PRIDE.SC'
namesOfFiles[1]='Ecoli_511145_strainK12_PRIDE.SC'
namesOfFiles[2]='ecoli1_HCD_CID_PRIDE.SC'
namesOfFiles[3]='Lu'
namesOfFiles[4]='Lewis_wt'
namesOfFiles[5]='Taniguchi'

#path='/local/eris/gabi/PaxDb/tmp/'
path='outputfiles/weightedFiles/511145_Ecoli/tmp'

#myMRNAfile='/local/eris/gabi/PaxDb/species/511145_Ecoli/outputfiles/weightedFiles_mRNAcorrelation_for6files_Ecoli.txt'
myMRNAfile='outputfiles/511145_Ecoli/weightedFiles_mRNAcorrelation_for6files_Ecoli.txt'

#beginning of tmp file names (cut it to get the scores)
mytmpFileName='all_511145_Ecoli-integrData_weighted_'

#outputpathname='/local/eris/gabi/PaxDb/species/511145_Ecoli/outputfiles/zscores_weightedFiles_allProteins.txt'
outputpathname='outputfiles/511145_Ecoli/zscores_weightedFiles_allProteins.txt'

getFittingMRNA='getFittingMRNACorrelation_6weights.pl'


## no more changes necessary

./bin/runGetScore_mRNA.sh $myMRNAfile $mytmpFileName $outputpathname $getFittingMRNA $path "${namesOfFiles[*]}"




