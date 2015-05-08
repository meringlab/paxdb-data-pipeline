# 
# Scoring based on a shared-protein-set:
# 1. For each protein (in the samples we want to combine)
#    compute the percentage in how many samples the protein exists. 
# 2. Take all the proteins that are in all the samples (100% ones).
# 3. If this set covers less than 30% of the proteome add more proteins
#    to the set (from higher to lower percentage) until:
#    - we hit the 30% of proteome in shared set.
#    - or the proteins will start covering less than 80% of samples.
#

import glob
import os
import shutil
import logging
import subprocess
import sys
import random
import re
import pickle
from os.path import join

import logger
from ruffus import ruffus
from paxdb import scores as scorer
from PaxDbDatasetsInfo import PaxDbDatasetsInfo, DatasetInfo


OUTPUT = '../output/v4.0/'
datasetsInfo = pickle.load(open(join(OUTPUT, 'paxdb_datasets_info.pickle'), 'rb'))

# THIS HAS TO RUN AFTER THE SPECTRAL COUNTING PIPELINE!
def compute_shared_proteins(species, organ, total_proteins):
    by_organ = datasetsInfo.datasets[species][organ]
    names = [os.path.splitext(d.dataset)[0] for d in by_organ if not d.integrated]
    if len(names) < 1:
        raise Error('failed to find datasets for {0}, {1}'.format(species, organ))
    proteins_count = dict()
    for d in names:
        num_abu = 0
        with open(join(OUTPUT, species, d + '.abu')) as abu:
            for line in abu:
                num_abu += 1
                r = line.split('\t')
                if not r[0] in proteins_count:
                    proteins_count[r[0]] = 0
                proteins_count[r[0]] += 1
        print('{0}% coverage {1}'.format(round(num_abu / total_proteins * 100), d))
    return proteins_count

if __name__ == '__main__':
    logger.configure_logging()
    for species in datasetsInfo.datasets:
        print('\n### {0} species'.format(species))
        for organ in datasetsInfo.datasets[species]:
            total_proteins =  datasetsInfo.datasets[species][organ][0].genome_size 
            print('\n# {0} datasets in {1}'.format(species, organ))
            proteins_counts = compute_shared_proteins(species, organ, total_proteins)

            coverage_proteins_count = dict()
            for p in proteins_counts:
                if not proteins_counts[p] in coverage_proteins_count:
                    coverage_proteins_count[proteins_counts[p]] = 0
                coverage_proteins_count[proteins_counts[p]] += 1

            cumulative=0
            for i in sorted(coverage_proteins_count, reverse = True):
                coverage_proteins_count[i] = coverage_proteins_count[i] / total_proteins
                cumulative += coverage_proteins_count[i] * 100
                print('proteins present in #{0} datasets cover {1}% of the proteome'.format(i, round(cumulative,2)))
    
