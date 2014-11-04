import glob
import os
import pickle
import shutil
import sys
from os.path import join
import logging

from paxdb import spectral_counting as sc, scores
from ruffus import ruffus
from paxdb.config import PaxDbConfig
from PaxDbDatasetsInfo import PaxDbDatasetsInfo
import logger


cfg = PaxDbConfig()

INPUT = join('../input', cfg.paxdb_version, "datasets/")
OUTPUT = join('../output', cfg.paxdb_version)
FASTA_DIR = '../input/' + cfg.paxdb_version + '/fasta'
FASTA_VER = cfg.fasta_version  # '10.0'

interactions_format = '../input/' + cfg.paxdb_version + '/interactions/{0}.network_v9_v10_900.txt'

#
# STAGE 1.1 spectral counting
#
@ruffus.mkdir(INPUT + '*/*.sc',
              ruffus.formatter(),
              OUTPUT + '/{subdir[0][0]}')
@ruffus.transform(INPUT + '*/*.sc',
                  ruffus.formatter(),
                  OUTPUT + '/{subdir[0][0]}/{basename[0]}.abu',
                  '{subdir[0][0]}')
def spectral_counting(input_file, output_file, species_id):
    sc.calculate_abundance_and_raw_spectral_counts(input_file, output_file, species_id, FASTA_DIR, FASTA_VER)


#
# STAGE 1.3
#
@ruffus.follows(spectral_counting)
@ruffus.transform(INPUT + '*/*.sc',
                  ruffus.formatter(),
                  OUTPUT + '/{subdir[0][0]}/{basename[0]}.peptide',
                  '{subdir[0][0]}')
def map_peptides(input_file, output_file, species_id):
    sc.map_peptide(input_file, output_file, species_id, FASTA_DIR, FASTA_VER)


#
# STAGE 1.2 just copy .abu to output
#
@ruffus.mkdir(INPUT + '*/*.abu',
              ruffus.formatter(),
              OUTPUT + '/{subdir[0][0]}')
@ruffus.transform(INPUT + '*/*.abu',
                  ruffus.formatter(),
                  OUTPUT + '/{subdir[0][0]}/{basename[0]}.abu')
def copy_abu_files(input_file, output_file):
    shutil.copyfile(input_file, output_file)


#
# STAGE 2 score original datasets
#
@ruffus.transform([spectral_counting, copy_abu_files],
                  ruffus.suffix(".abu"),
                  ".zscores")
def score(input_file, output_file):
    # get parent folder from input_file -> species_id
    # '../output/v4.0/9606/dataset.txt' -> 9606
    species_id = os.path.split(os.path.dirname(input_file))[1]
    if not species_id.isdigit():
        logging.error("failed to extract species id from ", input_file)
        raise ValueError("failed to extract species id from {0}".format(input_file))
    try:
        interactions_file = get_interactions_file(interactions_format, species_id)
    except ValueError as e:
        logging.error(e)
        return
    scores.score_dataset(input_file, output_file, interactions_file)


def get_interactions_file(interactions_format, speciesId):
    files = glob.glob(interactions_format.format(speciesId))
    if len(files) != 1:
        raise ValueError("failed to get interactions file for {0}".format(speciesId))
    interactions_file = files[0]
    if not os.path.isfile(interactions_file):
        raise ValueError("failed to get interactions file for {0}".format(speciesId))
    logging.debug('using %s', interactions_file)
    return interactions_file


def group_datasets_for_integration():
    try:
        return pickle.load(open('../output/datasets.pickle', 'rb'))
    except:
        logging.warning("failed to laod pickle", sys.exc_info()[0])
    datasets_to_integrate = []
    info = PaxDbDatasetsInfo()
    for species in info.datasets.keys():
        for organ in info.datasets[species].keys():
            if len(info.datasets[species][organ]) < 2:
                continue
            parameters = []
            parameters.append(
                [join(OUTPUT, species, os.path.splitext(d.dataset)[0] + '.abu') for d in info.datasets[species][organ]
                 if not d.integrated])
            integrated_dataset = [join(OUTPUT, species, os.path.splitext(d.dataset)[0] + '.integrated') for d in
                                  info.datasets[species][organ] if d.integrated]
            if not integrated_dataset:
                # not specified in the data info doc, so just make up one for now
                parameters.append("{0}-{1}.integrated".format(species, organ))
            else:
                parameters.append(integrated_dataset[0])
            parameters.append(species)
            parameters.append(organ)
            datasets_to_integrate.append(parameters)
    with open('../output/datasets.pickle', 'wb') as filedump:
        pickle.dump(datasets_to_integrate, filedump)
    return datasets_to_integrate


# STAGE 3 integrate datasets
#
# @ruffus.follows(score)
@ruffus.files(group_datasets_for_integration())
def integrate(input_files, output_file, species, organ):
    print('integrating {0}'.format(', '.join(input_files)))


#
# STAGE 4 score original datasets
#
@ruffus.follows(integrate)
@ruffus.transform(OUTPUT + "/*/*.integrated",
                  ruffus.suffix(".integrated"),
                  ".zscores")
def score_integrated(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")


# TODO mRNA

#
# STAGE, map identifiers to stringdb namespace
#
@ruffus.transform([spectral_counting, copy_abu_files],
                  ruffus.suffix(".abu"),
                  ".pax")
def map_to_stringdb_proteins(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")

# TODO Last STAGE write titles



if __name__ == '__main__':
    logger.configure_logging()
    ruffus.pipeline_printout(sys.stdout, [integrate], verbose_abbreviated_path=6, verbose=3)
    # ruffus.pipeline_run([integrate], verbose=3)

    # ruffus.pipeline_printout(sys.stdout, [score_integrated], verbose_abbreviated_path=6, verbose=6)
    # ruffus.pipeline_printout(sys.stdout, [map_to_stringdb_proteins, score], verbose_abbreviated_path=6,verbose=2)
    # ruffus.pipeline_run([map_peptides, score, integrate, score_integrated], verbose=3)

    # ruffus.pipeline_run([score, integrate, score_integrated], verbose=3)
