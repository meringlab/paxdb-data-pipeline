import os
import sys
from os.path import join

from ruffus import ruffus
from config import PaxDbConfig
from PaxDbDatasetsInfo import PaxDbDatasetsInfo
import logger


cfg = PaxDbConfig()

INPUT = join('../input', cfg.paxdb_version, "datasets/")
OUTPUT = join('../output', cfg.paxdb_version, 'datasets')


#
# STAGE 1.1 spectral counting
#
@ruffus.mkdir(INPUT + '*/*.sc',
              ruffus.formatter(),
              OUTPUT + '/{subdir[0][0]}')
@ruffus.transform(INPUT + '*/*.sc',
                  ruffus.formatter(),
                  OUTPUT + '/{subdir[0][0]}/{basename[0]}.abu')
def spectral_counting(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")


#
# STAGE 1.2 just copy .abu to output
#
@ruffus.mkdir(INPUT + '*/*.abu',
              ruffus.formatter(),
              OUTPUT + '/{subdir[0][0]}')
@ruffus.transform(INPUT + '*/*.abu',
                  ruffus.formatter(),
                  OUTPUT + '/{subdir[0][0]}/{basename[0]}.abu')
def copy_other_inputs(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")


#
# STAGE 2, map identifiers to stringdb namespace
#
@ruffus.transform([spectral_counting, copy_other_inputs],
                  ruffus.suffix(".abu"),
                  ".pax")
def map_to_stringdb_proteins(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")


#
# STAGE 3 score original datasets
#
@ruffus.transform([spectral_counting, copy_other_inputs],
                  ruffus.suffix(".abu"),
                  ".zscores")
def score(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")


def group_datasets_for_integration():
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
            parameters.append([join(OUTPUT, species, os.path.splitext(d.dataset)[0] + '.integrated') for d in
                               info.datasets[species][organ] if d.integrated][0])
            parameters.append(species)
            parameters.append(organ)
            datasets_to_integrate.append(parameters)
    return datasets_to_integrate


# STAGE 4 integrate datasets
#
@ruffus.follows(score)
@ruffus.files(group_datasets_for_integration())
def integrate(input_files, output_file, species, organ):
    print('integrating {0}'.format(', '.join(input_files)))
    oo = open(output_file, "w")


#
# STAGE 3 score original datasets
#
@ruffus.follows(integrate)
@ruffus.transform(OUTPUT + "/*/*.integrated",
                  ruffus.suffix(".zscores"),
                  ".zscores")
def score_integrated(input_file, output_file):
    ii = open(input_file)
    oo = open(output_file, "w")

# TODO mRNA
# TODO map integrated
# TODO write titles

if __name__ == '__main__':
    logger.configure_logging()
    ruffus.pipeline_printout(sys.stdout, [score_integrated], verbose_abbreviated_path=6, verbose=6)
    ruffus.pipeline_run([integrate], verbose=3)

    # ruffus.pipeline_printout(sys.stdout, [score_integrated], verbose_abbreviated_path=6, verbose=6)
    # ruffus.pipeline_printout(sys.stdout, [map_to_stringdb_proteins, score], verbose_abbreviated_path=6,verbose=2)
    # ruffus.pipeline_run([score_integrated], verbose=3)

    # ruffus.pipeline_run([score, integrate, score_integrated], verbose=3)
