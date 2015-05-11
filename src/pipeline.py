import glob
import os
import pickle
import re
import shutil
import sys
from os.path import join
import subprocess
import logging
from datetime import date

from DatasetIntegrator import DatasetIntegrator, RScriptRunner, species_mrna
from paxdb import spectral_counting as sc, scores
from ruffus import ruffus
from paxdb.config import PaxDbConfig
from PaxDbDatasetsInfo import PaxDbDatasetsInfo, DatasetInfo
import logger
import dataset
import sanity_check

cfg = PaxDbConfig()

INPUT = join('../input', cfg.paxdb_version, "datasets/")
OUTPUT = join('../output', cfg.paxdb_version)
FASTA_DIR = '../input/' + cfg.paxdb_version + '/fasta'
FASTA_VER = cfg.fasta_version  # '10.0'
STRINGDB_REPO = '../input/' + cfg.paxdb_version + '/stringdb/'
MRNA = join('../input', cfg.paxdb_version, "mrna/")

interactions_format = '../input/' + cfg.paxdb_version + '/interactions/{0}.network_v10_900.txt'

logger.configure_logging()

def parent_dir_to_species_id(input_file):
    # get parent folder from input_file -> species_id
    # '../output/v4.0/9606/dataset.txt' -> 9606
    species_id = os.path.split(os.path.dirname(input_file))[1]
    return species_id


def get_dataset_info_for_file(input_file):
    species_id = parent_dir_to_species_id(input_file)
    dataset_name = os.path.splitext(os.path.basename(input_file))[0]
    return datasetsInfo.get_dataset_info(species_id, dataset_name)


def get_interactions_file(interactions_format, speciesId):
    files = glob.glob(interactions_format.format(speciesId))
    if len(files) != 1:
        raise ValueError("failed to get interactions file for {0}".format(speciesId))
    interactions_file = files[0]
    if not os.path.isfile(interactions_file):
        raise ValueError("failed to get interactions file for {0}".format(speciesId))
    logging.debug('using %s', interactions_file)
    return interactions_file


def round_abundance(value):
    if type(value) == str:
        value = float(value);
    if value >= 100:
        return round(value);
    elif value >= 10:
        return round(value, 1)
    elif value >= 1:
        return round(value, 2)
    elif value >= 0.001:
        return round(value, 3);
    return 0;


try:
    datasetsInfo = pickle.load(open(join('../output', cfg.paxdb_version, 'paxdb_datasets_info.pickle'), 'rb'))
except IOError as e:
    datasetsInfo = PaxDbDatasetsInfo()
    pickle.dump(datasetsInfo, open(join('../output', cfg.paxdb_version, 'paxdb_datasets_info.pickle'), 'wb'))

sanity_check.datastsInfo_uptodate(datasetsInfo, INPUT, OUTPUT)
sanity_check.compile_java_if_necessary()
sanity_check.export_from_postgresql()

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

#@ruffus.follows(score)
@ruffus.mkdir([spectral_counting, copy_abu_files],
              ruffus.formatter(),
              OUTPUT + '/score_downsampled/{subdir[0][0]}')
@ruffus.follows(score)
@ruffus.transform([spectral_counting, copy_abu_files],
                  ruffus.formatter(),
                  OUTPUT + '/score_downsampled/{subdir[0][0]}/{basename[0]}{ext[0]}',
                  '{subdir[0][0]}')
def downsample(input_file, output_file, species):
    info = get_dataset_info_for_file(input_file)
    organ = info.organ
    datasets = [d for d in datasetsInfo.datasets[species][info.organ] if not d.integrated]
    if len(datasets) < 2:
        return

    total = datasetsInfo.datasets[species][organ][0].genome_size
    min_abundances = total
    sorted_abundances_map = dict()

    for d in datasets:
        sorted_abundances = sort_abundances(join(OUTPUT,species,to_abu_ext(d.dataset)))
        sorted_abundances_map[to_abu_ext(d.dataset)] = sorted_abundances
        total = datasetsInfo.datasets[species][organ][0].genome_size
        min_abundances = min(min_abundances, len(sorted_abundances))

    max_coverage = max(min_abundances, int(total * 0.3))

    downsample_dataset(sorted_abundances_map[os.path.basename(to_abu_ext(input_file))], max_coverage, output_file)

@ruffus.follows(downsample)
@ruffus.transform(OUTPUT +'/score_downsampled/*/*.abu',
                  ruffus.suffix(".abu"),
                  ".zscores")
def score_downsampled(input_file, output_file):
    score(input_file, output_file)


#
# FIXME: this will fail if a dataset exist in the info doc but not on the filesystem
def group_datasets_for_integration():
    '''
    Need to manually group datasets for ruffus; the alternative is to organize
    files on hard disk to be grouped by tissue/organ. 
    '''
    #mrna = species_mrna(MRNA)
    mrna = dict() # TODO we need to find new/updated mRNA data
    datasets_to_integrate = []

    sorter = scores.DatasetSorter()
    for species in datasetsInfo.datasets.keys():
        try:
            sorted_datasets = sorter.sort_datasets(join(OUTPUT, species))
        except:
            logging.error("failed to sort datasets for {0}: {1}".format(species, sys.exc_info()[1]))
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

            parameters.append(join(OUTPUT, species, "{0}-{1}-integrated.integrated".format(species, organ)))
            parameters.append(species)
            parameters.append(organ)
            yield parameters
            # datasets_to_integrate.append(parameters)
            # return datasets_to_integrate

def downsample_dataset(sorted_abundances, max_size, output_file):
    if os.path.exists(output_file):
        return
    num_abundances = len(sorted_abundances)
    if num_abundances > max_size:
        abundances = sorted_abundances[:max_size]
    else:
        abundances = sorted_abundances
    with open(output_file,'w') as abu:
        abu.writelines(abundances)

def read_score(score_file):
    with open(score_file) as s:
        return s.readline().strip()

def sort_abundances(dataset):
    cmd="cat '{0}'".format(dataset)
    cmd= cmd + "| awk '{print $2,$1}' | sort -gr  | awk '{print $2,$1}'"
    sorted_out = subprocess.check_output(cmd, shell=True).decode('utf8')
    sorted_abundances = [l +'\n' for l in sorted_out.split('\n')]
    return sorted_abundances


def to_abu_ext(datasetname):
    return os.path.splitext(datasetname)[0] + '.abu'

#
# naive scoring doesn't take dataset size into account when 
# deciding in which order to integrate datasets. So here we
# downsample to 30% (or min shared proteins if this is bigger than 30%).
#
# FIXME: this will fail if a dataset exist in the info doc but not on the filesystem
def group_datasets_for_integration_with_downsampling():
    '''
    Need to manually group datasets for ruffus; the alternative is to organize
    files on hard disk to be grouped by tissue/organ. 
    '''
    #mrna = species_mrna(MRNA) 
    mrna = dict() # TODO we need to find new/updated mRNA data
    datasets_to_integrate = []

    sorter = scores.DatasetSorter()
    for species in datasetsInfo.datasets.keys():
        for organ in datasetsInfo.datasets[species].keys():
            if len(datasetsInfo.datasets[species][organ]) < 2:
                continue
            try:
                sorted_datasets = sorter.sort_datasets(join(OUTPUT,'score_downsampled', species))
            except:
                logging.error("failed to sort datasets for {0}: {1}".format(species, sys.exc_info()[1]))
                continue

            parameters = []
            # sort by scores:
            by_organ = [os.path.splitext(d.dataset)[0] for d in datasetsInfo.datasets[species][organ] if
                        not d.integrated]
            parameters.append(
                [[join(OUTPUT, species, d + '.abu') for d in sorted_datasets if d in by_organ],
                 # dependency: zscores affect dataset integration order:
                 [join(OUTPUT, 'score_downsampled',species, d + '.zscores') for d in sorted_datasets if d in by_organ]
                ])
            # dependency: mRNA files:
            if species in mrna:
                parameters[0].append(mrna[species])

            parameters.append(join(OUTPUT, species, "{0}-{1}-integrated.integrated".format(species, organ)))
            parameters.append(species)
            parameters.append(organ)
            yield parameters
            # datasets_to_integrate.append(parameters)
            # return datasets_to_integrate


# STAGE 3 integrate datasets
#
@ruffus.follows(score)
@ruffus.files(group_datasets_for_integration_with_downsampling)
def integrate(input_list, output_file, species, organ):
    input_files = input_list[0]
    logging.debug('integrating {0}'.format(', '.join(input_files)))
    interactions_file = get_interactions_file(interactions_format, species)
    out_dir = join(OUTPUT, species) + '/'  # slash required ?
    if len(input_list) > 2:
        # TODO make R script accept args and pass mrna
        rscript = RScriptRunner('integrate_withMRNA.R', [input_list[2], out_dir])
    else:
        rscript = RScriptRunner('integrate.R', [out_dir])

    integrator = DatasetIntegrator(output_file, input_files, rscript, organ != 'WHOLE_ORGANISM')
    weights = integrator.integrate(interactions_file)
    logging.info(species + ' weights: ' + ','.join([str(w) for w in weights]))


#
# STAGE 4 score integrated datasets
#
@ruffus.follows(integrate)
@ruffus.transform(OUTPUT + "/*/*.integrated",
                  ruffus.suffix(".integrated"),
                  ".zscores")
def score_integrated(input_file, output_file):
    score(input_file, output_file)


#
# STAGE, TODO mRNA
#


#
# STAGE, map identifiers to stringdb namespace
#
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


# TODO use a template for this
def write_dataset_title(dst, info=DatasetInfo, dataset_score='1', dataset_weight='100', coverage='54%'):
    if not info.integrated:
        if info.condition_media:
            string1 = "#name: {0}, {1}, {2}, {3}\n".format(info.species_name, info.organ, info.condition_media,
                                                           info.publication.strip())
            string3 = "#description: abundance based on " + info.quantification_method + ", " + info.condition_media + ", " + "from<a href=\"" + info.source_link + "\" target=\"_blank\">" + info.publication.strip() + "</a><br/><b>Interaction consistency score</b>: " + dataset_score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
            title = "\'" + info.species_name + ", " + info.organ + ", " + info.condition_media + ", " + info.publication.strip() + "\'(weighting" + dataset_weight + "%)"
        else:
            string1 = "#name: " + info.species_name + ", " + info.organ + ", " + info.publication.strip() + "\n"
            string3 = "#description: abundance based on " + info.quantification_method + ", " + "from<a href=\"" + info.source_link + "\" target=\"_blank\">" + info.publication.strip() + "</a><br/><b>Interaction consistency score</b>: " + dataset_score + "&nbsp<b>Coverage</b>: " + coverage + "\n"
            title = "\'" + info.species_name + ", " + info.organ + ", " + info.publication.strip() + "\'(weighting" + dataset_weight + "%)"

        string2 = "#score: " + dataset_score + "\n" + "#weight: " + dataset_weight + "%\n"

        string4 = "#organ: " + info.organ + "\n" + "#integrated: false\n#coverage: " + coverage + '\n'
    else:
        string1 = "#name: " + info.species_name + ", " + info.organ + ", PaxDB integrated dataset\n"
        string2 = "#score: " + dataset_score + "\n" + "#weight: \n"

        # TODO once we have short names
        # lists_datasets = []
        # for d in datasetsInfo.datasets[species][info.organ]:
        # lists_datasets.append(d.name)

        string3 = "#description: integrated dataset: weighted average of all " + info.species_name + ' ' + info.organ + " datasets<br/><b>Interaction consistency score</b>: " + \
                  dataset_score + "&nbsp<b>Coverage</b>: " + coverage + "\n"

        string4 = "#organ: " + info.organ + "\n#integrated : true\n#coverage: " + coverage + '\n'

    dst.write(string1)
    dst.write(string2)
    dst.write(string3)
    dst.write(string4)
    dst.write("#publication_year: ")

    if info.integrated:
        dst.write(str(date.today().year))
    elif info.publication:
        m = re.match(r".+,\s*([0-9]{4})", info.publication)
        if m:
            yr = m.groups()[0]
            try:
                year = int(yr)
                if year > 1990 and year <= date.today().year:
                    dst.write(yr)
            except:
                logging.error("failed to get parse year for {0}".format(info.dataset))
    dst.write('\n')
    dst.write("#filename: " + os.path.splitext(info.dataset)[0] + ".txt\n")
    dst.write("#\n#internal_id\tstring_external_id\tabundance")
    if hasattr(info, 'quantification_method'):
        if info.quantification_method.lower().startswith("spectral counting"):
            dst.write("\traw_spectral_count")
    dst.write('\n')


@ruffus.transform([map_to_stringdb_proteins, map_integratedDs_to_stringdb_proteins],
                  ruffus.suffix(".pax"),
                  ".pax_rounded")
def round_abundances(input_file, output_file):
    with open(input_file) as src:
        with open(output_file, 'w') as dst:
            for line in src:
                rec = line.split('\t')
                rec[2] = (round_abundance(rec[2]))
                newline = '\t'.join([str(r) for r in rec])
                dst.write(newline)
                if not newline.endswith('\n'):
                    dst.write('\n')


# Last STAGE write titles
@ruffus.transform([round_abundances],
                  ruffus.suffix(".pax_rounded"),
                  ".txt")
def prepend_dataset_titles(input_file, output_file):
    species = parent_dir_to_species_id(input_file)
    try:
        info = get_dataset_info_for_file(input_file)
    except:  # assume integrated
        organ = os.path.splitext(os.path.basename(input_file).split('-')[1])[0]
        i = next(iter(datasetsInfo.datasets[species].values()))[0]  # any other dataset info
        info = type('DatasetInfo', (object,),
                    {'dataset': os.path.basename(output_file), 'integrated': True, 'species': species, 'organ': organ,
                     'genome_size': i.genome_size,
                     'species_name': i.species_name})()

    dataset_score = open(os.path.splitext(input_file)[0] + '.zscores').readline().strip()
    dataset_weight = get_dataset_weight(input_file)
    num_proteins = 0
    with open(input_file) as src:
        for line in src:
            num_proteins += 1
    coverage = str(round(100 * num_proteins / info.genome_size))

    with open(output_file, 'w') as dst:
        write_dataset_title(dst, info, dataset_score, dataset_weight, coverage)
        with open(input_file) as src:
            for line in src:
                dst.write(line)


if __name__ == '__main__':
    logger.configure_logging()
    #ruffus.pipeline_printout(sys.stdout, [score_integrated], verbose_abbreviated_path=6, verbose=3)
    ruffus.pipeline_run([score_integrated], verbose=3, multiprocess=60)
    #ruffus.pipeline_run([map_peptides, score, score_integrated, round_abundances, prepend_dataset_titles], verbose=3, multiprocess=40)
    #ruffus.pipeline_printout(sys.stdout, [map_peptides, score_integrated], verbose_abbreviated_path=6, verbose=3)
    #ruffus.pipeline_run([prepend_dataset_titles], verbose=3, multiprocess=1)

    # ruffus.pipeline_run([map_peptides, score, integrate, score_integrated, map_to_stringdb_proteins,
    # map_integratedDs_to_stringdb_proteins], verbose=3)
