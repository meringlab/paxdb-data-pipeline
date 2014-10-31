#!/usr/bin/python
#
# Input: 2-columns abundance files: [protein name <tab> abundance].
# 
# The script mirrors what Gabi was doing in her correlationDatasetsMRNA_*sh scripts.
#
# Author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
# Date: 24.09.2014.
from config import PaxDbConfig

cfg = PaxDbConfig()

# file with dataset names and respective scores
SCORES = "../output/" + cfg.paxdb_version + "/scores.txt"

OUTPUT = "../output/v4.0/correlations/"
INPUT = '../input/' + cfg.paxdb_version + '/'
MRNA = INPUT + 'mrna/'

from DatasetSorter import DatasetSorter
import os
import glob


def correlate(species, mrna, datasets_folder):
    print('correlating', species, 'using', mrna)
    sorter = DatasetSorter(SCORES)
    datasets = sorter.sort_datasets(datasets_folder)
    num_files = str(len(datasets))
    outfile = OUTPUT + species + '-mRNA__for' + num_files + 'files.txt'
    opts = ['--vanilla -q --slave', '-f', 'merge_and_correlate.R']
    args = ['--args', datasets_folder, mrna] + datasets
    import subprocess

    with open(outfile, 'w') as fileout:
        # XXX  http://stackoverflow.com/questions/11716923/python-interface-for-r-programming-language
        subprocess.call(['R'] + opts + args, stdout=fileout)


if __name__ == "__main__":
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)

    # only some species have mRNA data
    for mrna in glob.glob(MRNA + '*.txt'):
        try:
            #assume <speciesID>.txt format
            speciesID = int(os.path.splitext(os.path.basename(mrna))[0])
        except TypeError as e:
            print('ERROR, bad mrna file (wrong species id):', mrna, e)
            continue
        #path where are the datasets
        datasets_folder = INPUT + 'datasets/' + str(speciesID) + "/"
        correlate(str(speciesID), mrna, datasets_folder)
