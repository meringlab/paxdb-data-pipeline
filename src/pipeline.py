import os
import pickle
import shutil
import sys
from os.path import join
import logging

from ruffus import ruffus
from config import PaxDbConfig
from PaxDbDatasetsInfo import PaxDbDatasetsInfo
import logger
import spectral_counting as sc


cfg = PaxDbConfig()

INPUT = join('../input', cfg.paxdb_version, "datasets/")
OUTPUT = join('../output', cfg.paxdb_version)


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
    sc.calculate_abundance_and_raw_spectral_counts(input_file, output_file, species_id)

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
    ii = open(input_file)
    oo = open(output_file, "w")


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
@ruffus.follows(score)
@ruffus.files(group_datasets_for_integration())
def integrate(input_files, output_file, species, organ):
    print('integrating {0}'.format(', '.join(input_files)))
    oo = open(output_file, "w")


#
# STAGE 4 score original datasets
#
@ruffus.follows(integrate)
@ruffus.transform(OUTPUT + "/*/*.integrated",
                  ruffus.suffix(".zscores"),
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
    ruffus.pipeline_printout(sys.stdout, [spectral_counting], verbose_abbreviated_path=6, verbose=6)
    ruffus.pipeline_run([spectral_counting], verbose=3)

    # ruffus.pipeline_printout(sys.stdout, [score_integrated], verbose_abbreviated_path=6, verbose=6)
    # ruffus.pipeline_printout(sys.stdout, [map_to_stringdb_proteins, score], verbose_abbreviated_path=6,verbose=2)
    # ruffus.pipeline_run([score_integrated], verbose=3)

    # ruffus.pipeline_run([score, integrate, score_integrated], verbose=3)
