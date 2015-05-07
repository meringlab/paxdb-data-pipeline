# 
# let's see how the scoring formula behaves 
# when number of abundances goes down
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

datasetsInfo = pickle.load(open(join('../output/v4.0/paxdb_datasets_info.pickle'), 'rb'))

INPUT = '../input/v4.0/datasets/'
OUTPUT = '../output/v4.0/'

#SPECIES = '4932'
#TOTAL_PROTEINS = 6692 #read from db?
SPECIES = '9606'
TOTAL_PROTEINS = 20457
ORGAN = 'WHOLE_ORGANISM'
BATCH_SIZE=1000 # or 500 for smaller (3-6K) datasets

TMP = OUTPUT + 'scores_experiment/' + SPECIES + '/'
interactions_format = '../input/v4.0/interactions/{0}.network_v10_900.txt'

# THIS HAS TO RUN AFTER THE SPECTRAL COUNTING PIPELINE!
@ruffus.split(None, TMP + '*.abu')
def select_datasets_for_sampling(no_inputs, outputs):
    by_organ = datasetsInfo.datasets[SPECIES][ORGAN]
    names = [os.path.splitext(d.dataset)[0] for d in by_organ if not d.integrated]
    if len(names) < 1:
        raise Error('failed to find datasets for {0}, {1}'.format(SPECIES, ORGAN))
    for d in names:
        shutil.copy(join(OUTPUT, SPECIES, d + '.abu'), TMP)


@ruffus.follows(select_datasets_for_sampling)
@ruffus.split(TMP +'*.abu', TMP + '*.sample')
def sample_datasets(input_files, output_files):
    #
    #   clean up any files from previous runs
    #
    for ff in output_files:
        os.unlink(ff)
    
    for dataset in input_files:
        logging.debug('sampling %s', dataset)
        sorted_abundances = sort_abundances(dataset)
        total = len(sorted_abundances)

#        if total < TOTAL_PROTEINS / 3.3:
#            logging.info('skipping')
#            continue

        for num_removed in range(BATCH_SIZE, int(TOTAL_PROTEINS), BATCH_SIZE):
            if total <= num_removed:
                break
            dsname = os.path.splitext(os.path.basename(dataset))[0]
            output_file = TMP + dsname + '-random_' + str(total - num_removed) + '.sample'

            if not os.path.exists(output_file):
                abundances = random.sample(sorted_abundances, total - num_removed)
                with open(output_file,'w') as abu:
                    abu.writelines(abundances)

            #remove low-abundant:
            output_file = TMP + dsname + '-lowabundant_' + str(len(abundances)) + '.sample'
            if not os.path.exists(output_file):
                abundances = sorted_abundances[:int(total - num_removed)]
                with open(output_file,'w') as abu:
                    abu.writelines(abundances)

# remove by percent?
#
#        for percent in range(5,51, 5):
#            abundances = sorted_abundances[:int(total * (100.0-percent) / 100.0)]
#            tmp_score = score_subset(species, abundances)
#            logging.info('score for {0}%: {1}'.format(percent, tmp_score))
#            scores.append(tmp_score)

@ruffus.transform(sample_datasets, ruffus.suffix('.sample'), '.scores')
def score(input_file, output_file):
    logging.info('scoring {0} to {1}'.format(input_file, output_file))
    interactions_file = get_interactions_file(interactions_format, SPECIES)
    scorer.score_dataset(input_file, output_file, interactions_file)

@ruffus.follows(score)
@ruffus.transform(TMP + '*.abu',
                  ruffus.formatter(),
                  TMP + '{basename[0]}.csv')
def collect_scores(input_file, output_file):
    orig_score = read_score(join(OUTPUT, SPECIES, os.path.splitext(os.path.basename(input_file))[0] + '.zscores'))
    def get_num_removed(name):
        return int(re.match(r'.*-(lowabundant|random)_(\d+).scores',name).group(2))
    with open(output_file, 'w') as output:
        total = sum(1 for line in open(input_file))
        coverage = int(total * 100.0  / TOTAL_PROTEINS)
        output.write('# COVERAGE: {0}%\n'.format(coverage))
        output.write('# [0, 500, ...] low abundant proteins removed:\n')
        output.write(orig_score + ',')
        files = glob.glob(os.path.splitext(output_file)[0] + '-lowabundant*.scores')
        # MUST sort 
        files.sort(key= get_num_removed, reverse = True)
        for sc in files:
            output.write(read_score(sc) + ',')

        output.write('\n# [0, 500, ...] random proteins removed:\n')
        output.write(orig_score + ',')
        files = glob.glob(os.path.splitext(output_file)[0] + '-random*.scores')
        files.sort(key = get_num_removed, reverse = True)
        for sc in files:
            output.write(read_score(sc) + ',')
        output.write('\n')

def get_interactions_file(interactions_format, speciesId):
    files = glob.glob(interactions_format.format(speciesId))
    if len(files) != 1:
        raise ValueError("failed to get interactions file for {0}".format(speciesId))
    interactions_file = files[0]
    if not os.path.isfile(interactions_file):
        raise ValueError("failed to get interactions file for {0}".format(speciesId))
    logging.debug('using %s', interactions_file)
    return interactions_file

def read_score(score_file):
    with open(score_file) as s:
        return s.readline().strip()

def sort_abundances(dataset):
    cmd='cat ' + dataset
    cmd= cmd + "| awk '{print $2,$1}' | sort -gr  | awk '{print $2,$1}'"
    sorted_out = subprocess.check_output(cmd, shell=True).decode('utf8')
    sorted_abundances = [l +'\n' for l in sorted_out.split('\n')]
    return sorted_abundances


if __name__ == '__main__':
    logger.configure_logging()

    if not os.path.exists(TMP):
        os.makedirs(TMP)

    #ruffus.pipeline_printout(sys.stdout, [score, collect_scores], verbose_abbreviated_path=6, verbose=3)
    ruffus.pipeline_run([score, collect_scores], verbose=6, multiprocess=1)

#    shutil.rmtree(TMP)

