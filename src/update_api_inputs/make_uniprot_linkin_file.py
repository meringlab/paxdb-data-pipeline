## run in src/ dir
import yaml, os
import subprocess as sbp
import logging
from datetime import date

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename=f'../logs/{date.today().isoformat()}.log', format=FORMAT)


config_file = 'paxdb/config.yml'
with open(config_file) as f:
    config = yaml.load(f)
paxdb_version = config['VERSION']['PAXDB']

string_version = config['VERSION']['STRING']

with open(os.path.join('update_info', paxdb_version, 'species.yml')) as f:
    species = yaml.load(f)

download_dir = os.path.join(os.path.pardir, 'input', paxdb_version, 'alias')
if not os.path.isdir(download_dir):
    os.makedirs(download_dir)

for species_id in species:
    dst = os.path.join(download_dir, str(species_id)+'.protein.aliases.'+string_version+'.txt')
    src = dst+'.gz'
    if not os.path.isfile(dst):
        sbp.run(f'wget -O {src} "https://stringdb-static.org/download/protein.aliases.{string_version}/{species_id}.protein.aliases.{string_version}.txt.gz"; gunzip {src}; sleep 1', 
            shell = True)

output_file = f'version_update/{paxdb_version}/paxdb_uniprot_linkins_ids.tsv'
fw = open(output_file, 'w')
for species_id in species:
    try:
        with open(os.path.join(download_dir, str(species_id)+'.protein.aliases.'+string_version+'.txt')) as f:
            for l in f:
                if l.strip():
                    string_id, alias, source = l.strip().split('\t')
                    if source == 'BLAST_UniProt_ID':
                        print(string_id, alias, sep = '\t', file = fw)
    except FileNotFoundError:
        logging.error('Species ' + str(species_id) + ' has no alias file')
    except Exception as e:
        print(l, e)

fw.close()
