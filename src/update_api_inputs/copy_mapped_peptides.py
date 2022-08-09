### copy file with right name to mapped peptide folder for downloads
from os.path import join
import os, logging, re, shutil
from datetime import date

paxdb_version = 'v4.2'
FASTA_VER = '11.5'
root_dir = '/mnt/mnemo6/qingyao/paxDB/data-pipeline/'
output_dir = join(root_dir, 'output', paxdb_version)
download_dir = join(root_dir, 'output', paxdb_version, f'paxdb-mapped_peptides-{paxdb_version}')

if not os.path.isdir(download_dir):
    os.makedirs(download_dir)

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)
logger_file = logging.getLogger("write_log")
logger_file.addHandler(logging.FileHandler(f'{root_dir}/logs/{date.today().isoformat()}.log'))
logger_file.setLevel(30)

def get_species(filepath):
    species =  filepath.split('/')[-1]
    if not re.fullmatch('\d+', species):
        print(root)
        raise NameError("Did not find species")
    return species

for root,_,files in os.walk(output_dir):

    for f in files:
        if f.endswith('.peptide'):
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