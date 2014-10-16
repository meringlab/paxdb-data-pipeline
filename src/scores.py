#!/usr/bin/python
#
# Computes z-scores for all datasets. Requires libstatistics-descriptive-perl package installed (ubuntu)!
# 
#  For each dataset:
#   runs PaxDbScore*.pl 3 times, then takes the median
#
# Input files: 
#  1) abundance file: eris species/{species}/datasets/file.SC (ie ../species/9615/GPM_2012_09_Canis_familiaris.SC.txt)
#  2) interaction file: eris interactions/protein.links.v9.0.{species}_ncbi_900.txt (ie ../interactions/protein.links.v9.0.CanisFamiliaris_dog_9615_900.txt 
# 
# Output files:
#  * for each abundance file - a new one with zscores_ prepended to the name (ie zscores_file.SC)
# 
####
# Notes:
#
# Some input files had rows with only a single field (protein, no counts).
# To check if there are any use this command:
#   for i in *txt; do echo $i; awk '{ if (NF < 2) {printf ("%s\n", $1);exit;}}' $i; done
#
# To filter these lines out use this command:
#
#   awk '{ if (NF >= 2) printf ("%s\t%s\n", $1, $2);}' troublesome_file.txt > tmp; mv tmp troublesome_file.txt
#
# as a test I compared lines in troublesome_file.txt with 
#   $(cat troublesome_file.txt  | cut -f 2 | sort | grep -v '^$' | wc -l) 
# and looks like it works fine
# 
# 
# Originally written by Gabi in bash
# rewritten in python by Milan Simonovic <milan.simonovic@imls.uzh.ch>
# 

import logging
import logger
import os
import glob
import datetime
import subprocess
from config import PaxDbConfig
from os.path import join, isdir
from spectral_counting import keep_only_numbers_filter

cfg = PaxDbConfig()
# TODO use mapped files (need to strip species id from external id)
SPECTRAL_CTS_DIR='../output/'+cfg.paxdb_version+'/'
DIRECT_MAP_DIR='../input/'+cfg.paxdb_version+'/direct_mapping/'

pathOUT='../output/'+cfg.paxdb_version+'/zscores/'
if not isdir(pathOUT):
    os.mkdir(pathOUT)

# TODO interactions for StringDb v10 are not ready yet
#interactions='../input/'+cfg.paxdb_version+'/interactions/protein.links.v10.0.*_{0}_900.txt'
interactions_format='../input/v3.0/interactions/protein.links.v9.0.*_{0}_900.txt'

def run_scoring():
    logging.info("started scores computation at %s", datetime.datetime.now())
    spectral_cts_folders = sorted(filter(keep_only_numbers_filter, os.listdir(SPECTRAL_CTS_DIR)))
    direct_map_folders = sorted(filter(keep_only_numbers_filter, os.listdir(DIRECT_MAP_DIR)))

    logging.info("scoring spectral counting files for %s", str(spectral_cts_folders))
    for speciesId in spectral_cts_folders:
        logging.info("processing species %s", speciesId)
        interactions_file = get_interactions_file(speciesId)
        score_all_datasets(join(SPECTRAL_CTS_DIR, speciesId), 'SC', interactions_file)

    logging.info("scoring directly mapped files for %s", str(direct_map_folders))
    for speciesId in direct_map_folders:
        logging.info("processing species %s", speciesId)
        interactions_file = get_interactions_file(speciesId)
        score_all_datasets(join(DIRECT_MAP_DIR, speciesId), 'txt', interactions_file)

    # to cleanup failed files:
    #for i in */*; do num_lines=$(cat $i  | wc -l); if [ $num_lines -lt 4 ]; then rm $i; fi; done
    logging.info("done processing %s", datetime.datetime.now()) 

def get_interactions_file(speciesId):
    files=glob.glob(interactions_format.format(speciesId))
    if len(files) != 1:
        raise ValueError('failed to get interaction file {0}'.format(str(files)))
    logging.debug('using %s', files[0])
    return files[0]
    


def score_all_datasets(pathIN, extension, interactions_file):
    for d in glob.glob(join(pathIN, '*.'+extension)):
        logging.debug('abundance_file: %s', d)

    outfilename=('zscores_' + os.path.basename(d))
    outfilepath=join(pathOUT, outfilename)
    if os.path.isfile(outfilepath):
        logging.info('SKIPPING %s',outfilepath)
        continue
    logging.debug('output: %s',outfilepath)
    scores = compute_scores(d, interactions_file)
    #TODO update google doc!
    write_scores(d, scores, outfilepath)

def compute_scores(d, interactions_file):
    scores = []
    for i in range(1,4):  # @UnusedVariable
        try:
            cmd_out = subprocess.check_output(['perl', '-w', 'PaxDbScore_delta.pl', d, interactions_file])
            scores.append(float(cmd_out.strip()))
        except:
            logging.exception('failed to score %s',d)
            return
    logging.debug('scores: %s', str(scores))
    return scores


def write_scores(datafile, scores, outfilepath):
    if len(scores) != 3:
        logging.warn('%s scores missing, 3 expected: %s', datafile, str(scores))
        return

    with open(outfilepath, 'w') as output:
        output.write('# %s\n'.format(datetime.date.today().isoformat()))
        output.write('# %s\n'.format(datafile))
        output.write('\n'.join(map(lambda x: str(x), sorted(scores))))


if __name__ == '__main__':
    logger.configure_logging()
    run_scoring()
