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

from ruffus import ruffus
from paxdb import scores as scorer
import logger

INPUT = '../input/v4.0/datasets/'
OUTPUT = '../output/v4.0/'
TMP = OUTPUT + 'tmp/'
interactions_format = '../input/v4.0/interactions/{0}.network_v10_900.txt'

SPECIES = '4932'
TOTAL_PROTEINS = 6692 #read from db?

# THIS HAS TO RUN AFTER THE SPECTRAL COUNTING PIPELINE!
@ruffus.split(OUTPUT + SPECIES + '/*.abu', TMP + '*.abu')
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

#        if total < total_proteins / 3.3:
#            logging.info('skipping')
#            continue

        for num_removed in range(500, int(total_proteins), 500):
            if total <= num_removed:
                break
            dsname = os.path.splitext(os.path.basename(dataset))[0]
            output_file = TMP + dsname + '-random_' + str(total - num_removed) + '.abu'

            if not os.path.exists(output_file):
                abundances = random.sample(sorted_abundances, total - num_removed)
                with open(output_file,'w') as abu:
                    abu.writelines(abundances)

            #remove low-abundant:
            output_file = TMP + dsname + '-lowabundant_' + str(len(abundances)) + '.abu'
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

@ruffus.transform(sample_datasets, ruffus.suffix('.abu'), '.scores')
def score(input_file, output_file):
    logging.info('scoring {0} to {1}'.format(input_file, output_file))
    interactions_file = get_interactions_file(interactions_format, SPECIES)
    scorer.score_dataset(input_file, output_file, interactions_file)

@ruffus.follows(score)
@ruffus.transform(OUTPUT + SPECIES + '/*.abu', 
                  ruffus.formatter(),
                  TMP + '{basename[0]}.csv')
def collect_scores(input_file, output_file):
    orig_score = read_score(os.path.splitext(input_file)[0] + '.zscores')
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
        os.mkdir(TMP)

    #ruffus.pipeline_printout(sys.stdout, [score], verbose_abbreviated_path=6, verbose=3)

    ruffus.pipeline_run([score, collect_scores], verbose=6, multiprocess=1)

#    shutil.rmtree(TMP)

