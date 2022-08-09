### output a table to paste into google sheets with info of added datasets
### columns definitely required (in order):
### species_id,species,dataset,_,_,_,genome_size,organ,integrated,"publication/source","source_link" 
### (the two columns in quotes should be manually added)

import os, re, yaml, logging
import psycopg2
from paxdb.config import PaxDbConfig

new_data_dir_name = 'new'
config_file = 'paxdb/config.yml'
with open(config_file) as f:
    config = yaml.load(f)
paxdb_version = config['VERSION']['PAXDB']
species_path = config['FILE_PATHS']['SPECIES_INFO']

speID_size = {}
with open(species_path) as f:
    for l in f:
        speID = l.split()[0]
        size = l.split()[-1]
        speID_size[speID] = size

cfg = PaxDbConfig()
DB_URL = cfg.pg_url

input_dir = f'../../input/{new_data_dir_name}/datasets/'
output_dir = '../version_update/' + paxdb_version + '/'
output_whole_organism_path = output_dir + 'dataset_info_whole.tsv'
output_organ_path = output_dir + 'dataset_info_organ.tsv'
dbcon = psycopg2.connect(DB_URL)
# to properly handle unicode (see http://initd.org/psycopg/docs/usage.html#unicode-handling):
dbcon.set_client_encoding('UTF8')

cur = dbcon.cursor()

def get_species(filepath):
    species =  filepath.split('/')[-1]
    if not re.fullmatch('\d+', species):
        raise NameError("Did not find species")
    return species

def get_organ(filename, species_names):
    """
    based on the first segment of the files name split by underscore (_)
    the last word in that segment should be organ if it's not the species/subspecies name,
    and if it's not also the first word (like human)
    """
    firstSegment = filename.split('_')[0]
    words = firstSegment.split('-')
    if len(words) == 1:
        return 'whole_organism'

    else:
        candicate = words[-1]

        if candicate in species_names:
            return 'whole_organism'

        else:
            return candicate

info = []
for root, _, files in os.walk(input_dir):
    for f in files:
        if f.endswith('.sc') or f.endswith('.abu'):
            try:
                species = get_species(root)
            except NameError:
                logging.error(root + ': no species in path')
                continue
            cur.execute("SELECT species_id, compact_name "
                        "FROM {}.proteins "
                        "WHERE species_id={}".format
                        (cfg.paxdb_version_sql, species))
            for s in cur:
                species_name = s[1]
                break
            potential_names = [j for i in species_name.split('.') for j in i.split()]
            organ = get_organ(f, potential_names)
            score_dir = root.replace('input','output').replace('datasets/','')
            score_file = os.path.join(score_dir, os.path.splitext(f)[0]+'.zscores')
            if os.path.exists(score_file):
                with open(score_file) as score_f:
                    score = score_f.readline()
            else:
                score = ''
            info.append([species, species_name, f, score, '', '', speID_size[species], organ, 'N'])

output_table = ''
with open(output_whole_organism_path, 'w') as fw:
    with open(output_organ_path, 'w') as fo:
        for l in info:
            if l[-1] == 'whole_organism':
                print('\t'.join(l), file = fw)
            else:
                print('\t'.join(l), file = fo)