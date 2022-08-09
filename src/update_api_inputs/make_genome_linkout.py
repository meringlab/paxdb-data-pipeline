# construct eggnog5_genome_linkout.txt for paxdb-api
import yaml, os
from bs4 import BeautifulSoup
import urllib
import time

def get_ensembl_version(name):
    try:
        link = f"http://www.ensembl.org/{'_'.join(name.split())}/Info/Index?db=core"
        with urllib.request.urlopen(link) as f:
            soup = BeautifulSoup(f.read(300))
            version = soup.title.string.split()[-1]
            time.sleep(0.5)
            return link, 'Ensembl', ' release ' + version
    except:

        try:
            link = f"http://plants.ensembl.org/{'_'.join(name.split())}/Info/Index?db=core"
            with urllib.request.urlopen(link) as f:
                soup = BeautifulSoup(f.read(300))
                version = soup.title.string.split()[-1]
                time.sleep(0.5)
                return link, 'Ensembl Plants', ' release ' + version
        except:
            
            
            try:
                link = f"http://protists.ensembl.org/{'_'.join(name.split())}/Info/Index?db=core"
                with urllib.request.urlopen(link) as f:
                    soup = BeautifulSoup(f.read(300))
                    version = soup.title.string.split()[-1]
                    time.sleep(0.5)
                    return link, 'Ensembl Protists', ' release ' + version
            except:  
            
                try:
                    link = f"http://fungi.ensembl.org/{'_'.join(name.split())}/Info/Index?db=core"
                    with urllib.request.urlopen(link) as f:
                        soup = BeautifulSoup(f.read(300))
                        version = soup.title.string.split()[-1]
                        time.sleep(0.5)
                        return link, 'Ensembl Fungi', 'release ' + version
                except:

                    try:
                        link = f"http://metazoa.ensembl.org/{'_'.join(name.split())}/Info/Index?db=core"
                        with urllib.request.urlopen(link) as f:
                            soup = BeautifulSoup(f.read(300))
                            version = soup.title.string.split()[-1]
                            time.sleep(0.5)
                            return link, 'Ensembl Metazoa', 'release ' + version

                    except:
                        return '', '' ,''

    

if __name__ == '__main__':
    config_file = '../paxdb/config.yml'
    with open(config_file) as f:
        config = yaml.load(f)
    paxdb_version = config['VERSION']['PAXDB']
    eggnog_version = config['VERSION']['EGGNOG']
    string_version = config['VERSION']['STRING']
    species = config['SPECIES_IDS']

    species_file = f'/mnt/mnemo6/damian/STRING_derived_{string_version}/download_files/species.{string_version}.txt'
    output_file = f'../version_update/{paxdb_version}/eggnog{eggnog_version}_genome_linkout.txt'
    
    with open(output_file, 'w') as fw:
        with open(species_file) as f:
            next(f)
            for l in f:
                taxonid =  l.split('\t')[0]
                if int(taxonid) in species:
                    print(taxonid)
                    name = l.split('\t')[3]
                    link, repo, version = get_ensembl_version(name)
                    if link == '':
                        link = f'http://www.ncbi.nlm.nih.gov/genome/?term=txid{taxonid}[Organism:noexp]'
                        repo = 'Refseq'
                    print(name, taxonid, repo, version, link, '_'.join(name.split()), sep = '\t', file = fw)
