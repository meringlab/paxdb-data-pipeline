## rsync -hav paxdb-uniprot-crossreferences.txt pisces.meringlab.org:/home/qingyao/paxdb_nginx/html/downloads/5.0/
## 
import sys, os, yaml
import subprocess as sbp
sys.path.append('..')
from stringdb.repository import StringDbFileRepository

config_file = '../paxdb/config.yml'
with open(config_file) as f:
    config = yaml.load(f)
paxdb_version = config['VERSION']['PAXDB']
string_version = config['VERSION']['STRING']

root_dir = '/mnt/mnemo6/qingyao/paxDB/data-pipeline/'

with open(os.path.join('../version_update', paxdb_version, 'species.yml')) as f:
    species = yaml.load(f)

download_dir = os.path.join('../../input', paxdb_version, 'alias')
if not os.path.isdir(download_dir):
    os.makedirs(download_dir)

for species_id in species:
    dst = os.path.join(download_dir, str(species_id)+'.protein.aliases.'+string_version+'.txt')
    src = dst+'.gz'
    if not os.path.isfile(dst):
        sbp.run(f'wget -O {src} "https://stringdb-static.org/download/protein.aliases.{string_version}/{species_id}.protein.aliases.{string_version}.txt.gz"; gunzip {src}; sleep 1', 
            shell = True)

output_file = f'../version_update/{paxdb_version}/paxdb-uniprot-crossreferences.txt'
fw = open(output_file, 'w')
for species_id in species:
    print(species_id)
    try:
        with open(os.path.join(download_dir, str(species_id)+'.protein.aliases.'+string_version+'.txt')) as f:
            for l in f:
                if l.strip():
                    string_id, alias, source = l.strip().split('\t')
                    if source == 'BLAST_UniProt_AC':
                        print(alias, string_id.replace('.','-',1), sep = '\t', file = fw)
    except FileNotFoundError:
        print('Species ' + str(species_id) + ' has no alias file')
    except Exception as e:
        print(l, e)

fw.close()