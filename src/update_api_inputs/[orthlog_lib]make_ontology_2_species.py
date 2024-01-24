## input for paxdb-orthology-lib npm library
import os, sys
version_no = 'v5.0'
sys.path.append('../gspread')
sys.path.append('..')

from PaxDbDatasetsInfo import PaxDbDatasetsInfo

out_dir = f'../version_update/{version_no}/'

datasetsInfo = PaxDbDatasetsInfo()
with open(os.path.join(out_dir,'ontology_2_species.tsv'), 'w') as wf:
    for i,j in datasetsInfo.get_species_organ():
        print(i, j, sep = '\t', file = wf)
