import glob
import os
import pickle
import re
import shutil
import sys
from os.path import join
import logging

from DatasetIntegrator import DatasetIntegrator, RScriptRunner, species_mrna
from paxdb import spectral_counting as sc, scores
from ruffus import ruffus
from paxdb.config import PaxDbConfig
from PaxDbDatasetsInfo import PaxDbDatasetsInfo, DatasetInfo
import logger
import dataset


cfg = PaxDbConfig()

INPUT = join('../input', cfg.paxdb_version, "datasets/")
OUTPUT = join('../output', cfg.paxdb_version)
FASTA_DIR = '../input/' + cfg.paxdb_version + '/fasta'
FASTA_VER = cfg.fasta_version  # '10.0'
STRINGDB_REPO = '../input/' + cfg.paxdb_version + '/stringdb/'
MRNA = join('../input', cfg.paxdb_version, "mrna/")

interactions_format = '../input/' + cfg.paxdb_version + '/interactions/{0}.network_v9_v10_900.txt'

try:
    datasetsInfo = pickle.load(open(join('../output', cfg.paxdb_version, 'paxdb_datasets_info.pickle'), 'rb'))
except IOError as e:
    datasetsInfo = PaxDbDatasetsInfo()
    pickle.dump(datasetsInfo, open(join('../output', cfg.paxdb_version, 'paxdb_datasets_info.pickle'), 'wb'))


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
    species_id = parent_dir_to_species_id(input_file)
    if not species_id.isdigit():
        logging.error("failed to extract species id from ", input_file)
        raise ValueError("failed to extract species id from {0}".format(input_file))
    interactions_file = get_interactions_file(interactions_format, species_id)
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


#
# FIXME: this requires scores to sort datasets, but it's run before the scoring starts!
# to fix it: after running the score step, the info doc should be updated, pickled files
# deleted and datasets grouped for integration again.
# The workaround is: run scoring, stop the pipeline, delete the pickled file, and then
# continue the pipeline.
#
def group_datasets_for_integration():
    integrated_pickle = join('../output', cfg.paxdb_version, 'datasets_to_integrate.pickle')
    try:
        return pickle.load(open(integrated_pickle, 'rb'))
    except:
        pass
        # logging.warning("failed to load pickle", sys.exc_info()[0])
    mrna = species_mrna(MRNA)
    datasets_to_integrate = []

    sorter = scores.DatasetSorter()
    for species in datasetsInfo.datasets.keys():
        try:
            sorted_datasets = sorter.sort_datasets(join(OUTPUT, species))
        except:
            logging.error("failed to sort datasets for {0}".format(species), sys.exc_info())
            continue
        for organ in datasetsInfo.datasets[species].keys():
            if len(datasetsInfo.datasets[species][organ]) < 2:
                continue
            parameters = []
            # sort by scores:
            by_organ = [os.path.splitext(d.dataset)[0] for d in datasetsInfo.datasets[species][organ] if
                        not d.integrated]
            parameters.append(
                [[join(OUTPUT, species, d + '.abu') for d in sorted_datasets if d in by_organ],
                 # dependency: zscores affect dataset integration order:
                 [join(OUTPUT, species, d + '.zscores') for d in sorted_datasets if d in by_organ]
                ])
            # dependency: mRNA files:
            if species in mrna:
                parameters[0].append(mrna[species])
            integrated_dataset = [join(OUTPUT, species, os.path.splitext(d.dataset)[0] + '.integrated') for d in
                                  datasetsInfo.datasets[species][organ] if d.integrated]
            if not integrated_dataset:
                # not specified in the data info doc, so just make up one for now
                parameters.append("{0}-{1}.integrated".format(species, organ))
            else:
                parameters.append(integrated_dataset[0])
            parameters.append(species)
            parameters.append(organ)
            datasets_to_integrate.append(parameters)
    with open(integrated_pickle, 'wb') as filedump:
        pickle.dump(datasets_to_integrate, filedump)
    return datasets_to_integrate


# STAGE 3 integrate datasets
#
@ruffus.follows(score)
@ruffus.files(group_datasets_for_integration())
def integrate(input_list, output_file, species, organ):
    input_files = input_list[0]
    logging.debug('integrating {0}'.format(', '.join(input_files)))
    interactions_file = get_interactions_file(interactions_format, species)
    out_dir = os.path.dirname(output_file) + '/'  # slash required
    if len(input_list) > 2:
        # TODO make R script accept args and pass mrna
        rscript = RScriptRunner('integrate_withMRNA.R', [input_list[2], out_dir])
    else:
        rscript = RScriptRunner('integrate.R', [out_dir])

    integrator = DatasetIntegrator(output_file, input_files, rscript)
    weights = integrator.integrate(interactions_file)
    logging.info(species + ' weights: ' + ','.join([str(w) for w in weights]))


#
# STAGE 4 score original datasets
#
@ruffus.follows(integrate)
@ruffus.transform(OUTPUT + "/*/*.integrated",
                  ruffus.suffix(".integrated"),
                  ".zscores")
def score_integrated(input_file, output_file):
    score(input_file, output_file)


# TODO mRNA

#
# STAGE, map identifiers to stringdb namespace
#
def parent_dir_to_species_id(input_file):
    # get parent folder from input_file -> species_id
    # '../output/v4.0/9606/dataset.txt' -> 9606
    species_id = os.path.split(os.path.dirname(input_file))[1]
    return species_id


@ruffus.transform([spectral_counting, copy_abu_files],
                  ruffus.suffix(".abu"),
                  ".pax")
def map_to_stringdb_proteins(input_file, output_file):
    species_id = parent_dir_to_species_id(input_file)
    dataset.map_dataset(species_id, input_file, output_file, STRINGDB_REPO)


@ruffus.transform([integrate],
                  ruffus.suffix(".integrated"),
                  ".pax")
def map_integratedDs_to_stringdb_proteins(input_file, output_file):
    map_to_stringdb_proteins(input_file, output_file)


def get_dataset_info(input_file):
    species_id = parent_dir_to_species_id(input_file)
    dataset_name = os.path.splitext(os.path.basename(input_file))[0]
    by_organ = datasetsInfo.datasets[species_id]
    for organ in by_organ:
        for d in by_organ[organ]:
            if dataset_name == os.path.splitext(d.dataset)[0]:
                return d
    raise ValueError("no dataset info for %s", input_file)


def get_dataset_weight(input_file):
    dataset_name = os.path.splitext(os.path.basename(input_file))[0]
    for weights in glob.glob(os.path.dirname(input_file) + '/*.weights'):
        with open(weights) as weight_file:
            for line in weight_file:
                if line.startswith(dataset_name):
                    return line.split(":")[1].strip()
    # ("no dataset weight for %s", input_file)
    # not all datasets will have computed weights,
    # only when there're more than one for a given organ
    return '100'


def write_dataset_title(dst, info=DatasetInfo, dataset_score='1', dataset_weight='100', coverage='54%'):
    if not info.integrated:
        if info.condition_media:
            string1 = "#name: {0}, {1}, {2}, {3}\n".format(info.species_name, info.organ, info.condition_media,
                                                           info.publication)
            string3 = "#description: abundance based on " + info.quantification_method + ", " + info.condition_media + ", " + "from<a href=\"" + info.source_link + "\" target=\"_blank\">" + info.publication + "</a><br/><b>Interaction consistency score</b>: " + dataset_score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
            title = "\'" + info.species_name + ", " + info.organ + ", " + info.condition_media + ", " + info.publication + "\'(weighting" + dataset_weight + "%)"
        else:
            string1 = "#name: " + info.species_name + ", " + info.organ + ", " + info.publication + "\n"
            string3 = "#description: abundance based on " + info.quantification_method + ", " + "from<a href=\"" + info.source_link + "\" target=\"_blank\">" + info.publication + "</a><br/><b>Interaction consistency score</b>: " + dataset_score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
            title = "\'" + info.species_name + ", " + info.organ + ", " + info.publication + "\'(weighting" + dataset_weight + "%)"

        string2 = "#score: " + dataset_score + "\n" + "#weight: " + dataset_weight + "%\n"

        string4 = "#organ: " + info.organ + "\n" + "#integrated: false\n#\n" + "#internal_id\tstring_external_id\tabundance_ppm"
        if info.quantification_method and info.quantification_method.lower().startswith("spectral counting"):
            string4 = string4 + "\traw_spectral_count"
        string4 = string4 + "\n#\n"

    else:
        string1 = "#name: " + info.species_name + ", " + info.organ + ", PaxDB integrated dataset\n"
        string2 = "#score: " + dataset_score + "\n" + "#weight: \n"

        string3 = "#description: integrated dataset: weighted average of " \
                  + 'TODO_lists_datasets' + "<br/><b>Interaction consistency score</b>: " + \
                  dataset_score + "&nbsp<b>Coverage</b>: " + coverage + "\n"

        string4 = "#organ: " + info.organ + "\n#integrated : true\n#\n#internal_id\tstring_external_id\tabundance\n#\n"

    dst.write(string1)
    dst.write(string2)
    dst.write(string3)
    dst.write(string4)
    dst.write("#publication_year: ")
    m = re.match(r".+,\s*([0-9]{4})", info.publication)
    if m:
        dst.write(m[0])
    elif info.integrated:
        from datetime import date

        dst.write(str(date.today().year))
    dst.write('\n')


# Last STAGE write titles
@ruffus.transform([map_to_stringdb_proteins, map_integratedDs_to_stringdb_proteins],
                  ruffus.suffix(".pax"),
                  ".txt")
def prepend_dataset_titles(input_file, output_file):
    info = get_dataset_info(input_file)
    dataset_score = open(os.path.splitext(input_file)[0] + '.zscores').readline().strip()
    dataset_weight = get_dataset_weight(input_file)
    num_proteins = 0
    with open(input_file) as src:
        for line in src:
            num_proteins = num_proteins + 1
    coverage = str(100 * num_proteins / info.genome_size)

    with open(output_file, 'w') as dst:
        write_dataset_title(dst, info, dataset_score, dataset_weight, coverage)
        with open(input_file) as src:
            for line in src:
                dst.write(line)


if __name__ == '__main__':
    logger.configure_logging()
    # ruffus.pipeline_printout(sys.stdout, [score], verbose_abbreviated_path=6, verbose=3)
    ruffus.pipeline_run([score], verbose=3, multiprocess=4)

    # ruffus.pipeline_run([map_peptides, score, integrate, score_integrated, map_to_stringdb_proteins,
    # map_integratedDs_to_stringdb_proteins], verbose=3)
