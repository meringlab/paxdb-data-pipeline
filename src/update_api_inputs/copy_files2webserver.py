from os.path import join
import os, logging, re, shutil
from datetime import date

import yaml, sys
config_file = '../paxdb/config.yml'

with open(config_file) as f:
    config = yaml.safe_load(f)

def get_species(filepath):
    species =  filepath.split('/')[-1]
    if not re.fullmatch('\d+', species):
        print(root)
        raise NameError("Did not find species")
    return species
if __name__ == '__main__':
    step = sys.argv[1]
    paxdb_version = sys.argv[2]
    
    
    # paxdb_version = config['VERSION']['PAXDB']
    FASTA_VER = config['VERSION']['STRING']
    root_dir = '/mnt/mnemo6/qingyao/paxDB/data-pipeline/'
    output_dir = join(root_dir, 'output', paxdb_version)
    input_dir = join(root_dir, 'input', paxdb_version)
    download_dir = join(root_dir, 'output', paxdb_version, f'paxdb-mapped_peptides-{paxdb_version}')

    ### copy file with right name to mapped peptide folder for downloads
    if step == '1':
        ## if last version uses same string version and processed files are copied, else remove this copytree step
        last_version = sys.argv[3] 
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)
        shutil.copytree(join(root_dir, 'output', last_version, f'paxdb-mapped_peptides-{last_version}'), download_dir)
        
        if not os.path.isdir(download_dir):
            os.makedirs(download_dir)
        
        FORMAT = '%(asctime)s %(levelname)s %(message)s'
        logging.basicConfig(format=FORMAT)
        logger_file = logging.getLogger("write_log")
        logger_file.addHandler(logging.FileHandler(f'{root_dir}/logs/{date.today().isoformat()}.log'))
        logger_file.setLevel(30)
        for root,_,files in os.walk(output_dir):

            if f'paxdb-mapped_peptides-{paxdb_version}' in root:
                continue
            for f in files:
                if f.endswith('.peptide') or f.endswith('.peptide_int'):
                    try:
                        species = get_species(root)
                    except NameError:
                        logger_file.error('.txt file: ' + f + ': no species found.')
                        continue

                    if f.startswith(species):
                        output_file = join(download_dir,f.replace(species+'_', species+'-'))
                    else:
                        output_file = join(download_dir,species+'-'+f)
                    
                    shutil.copyfile(join(root, f), output_file)
        
        
    ### print shell command to copy files to the web server
    if step == '2':
        web_server = sys.argv[3]
        download_location = sys.argv[4]
        print(f'rsync -hav {output_dir}/downloads/ {web_server}:{download_location}/datasets/')
        print()
        print(f'rsync -hav {output_dir}/paxdb-mapped_peptides-{paxdb_version} {web_server}:{download_location}/')
        print()
        print(f'scp ../version_update/{paxdb_version}/paxdb_uniprot_linkins_ids.tsv {web_server}:{download_location}/paxdb-uniprot-links-{paxdb_version}.tsv')
        print()
        print(f'rsync -hav --include="*orthologs.txt" --exclude="pruned/" --exclude="*" ../version_update/{paxdb_version}/orthgroups/ {web_server}:{download_location}/paxdb-orthologs-{paxdb_version}/')
        print()
        print(f'rsync -hav --exclude="fetch.*" {input_dir}/fasta/ {web_server}:{download_location}/paxdb-protein-sequences-{paxdb_version}/')