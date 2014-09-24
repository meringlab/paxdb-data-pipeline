#!/usr/bin/python
#
# Input: 2-columns abundance files: [protein name <tab> abundance].
# 
# The script mirrors what Gabi was doing in her correlationDatasetsMRNA_*sh scripts.
#  
# Author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
# Date: 24.09.2014.

# file with dataset names and respective scores
SCORES="../output/v3.1/scores.txt"

OUTPUT="../output/v3.1/correlations/"
INPUT='../input/v3.1/'
MRNA=INPUT+'mrna/'

import os
from os import listdir
from os.path import isfile, join
import sys
import glob

def read_scores():
    with open(SCORES) as f:
        scores = dict()
        for line in f:
            r = [r.strip() for r in line.split('\t') if len(r.strip()) >0]
            if len(r) > 1:
                # without extension since it's easier than keepin track if its SC,txt, out...
                scores[os.path.splitext(r[0])[0]] = float(r[1])
    if len(scores) == 0:
        raise Exception('no scores found in ' + SCORES)
    return scores
 
# FIXME: needs global var scores! need a lambda to close on ...
def get_dataset_score(d):
    name=os.path.splitext(d)[0]
    if scores.has_key(name):
        return scores[name]
    print 'WARN, no score for',d
    return -sys.maxint -1 #just put it at the end 

def sort_datasets(folder):
    datasets = [ f for f in listdir(folder) if isfile(join(folder,f)) ]
    if len(datasets) == 0:
        raise Exception('no datasets found in ' + folder)
    by_score = sorted(datasets, key=get_dataset_score)
    by_score.reverse()
    return by_score
    
    
def correlate(species, mrna, datasets_folder):
    print 'correlating',species,'using',mrna
    datasets=sort_datasets(datasets_folder)
    num_files=str(len(datasets))
    outfile=OUTPUT+species+'-mRNA__for'+num_files+'files.txt'
    opts=['--vanilla -q --slave','-f', 'merge_and_correlate.R']
    args=['--args', datasets_folder, mrna] + datasets
    import subprocess
    with open(outfile, 'w') as fileout:
        subprocess.call(['R'] + opts + args, stdout=fileout)
# TODO http://stackoverflow.com/questions/11716923/python-interface-for-r-programming-language

if not os.path.exists(OUTPUT):
    os.mkdir(OUTPUT)

scores = read_scores()

# only some species have mRNA data
for mrna in glob.glob(MRNA + '*.txt'):
    try:
        #assume <speciesID>.txt format
        speciesID = int(os.path.splitext(os.path.basename(mrna))[0])
    except TypeError as e:
        print 'ERROR, bad mrna file (wrong species id):',mrna, e
        continue
    #path where are the datasets
    datasets_folder=INPUT + 'datasets/' + str(speciesID) + "/"
    correlate(str(speciesID), mrna, datasets_folder)
