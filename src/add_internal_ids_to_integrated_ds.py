#!/usr/bin/python

from os.path import join
import shutil

import spectral_counting as mapper
from config import PaxDbConfig


cfg = PaxDbConfig()

folder = '../input/' + cfg.paxdb_version + '/datasets'
files = '''./9606/human_lungProteins_Abdul-Salam_2010_Circulation_PeptideIonIntensityValues_abu.txt
./9606/Human_heart_ThinThinAye_MolecularBioSystems2010_APEX.txt
./9606/Human_liver_Chinese_2010_J._Proteome_Res.txt
./4896/pombe_cell2012_protein.txt
./511145/Taniguchi_2010_Table_S6.txt
./511145/Lu_ecoli_2007.txt
./10090/mouse_lung_kislinger2006_cell.txt
./10090/mouse_liver_kislinger2006_cell.txt
./10090/mouse_glomeruli_kidney_F.Waanders2009_PNAs.txt
./10090/mouse_brain_kislinger2006_cell.txt
./10090/mouse_kidney_kislinger2006_cell.txt
./10090/mouse_placenta_kislinger2006_cell.txt
./10090/mouse_heart_kislinger2006_cell.txt
./10090/mouse_pancreas_F.Waanders2009_PNAs_combine.txt
./4932/Ghaemmaghami_et_al_yeast_data.txt
./4932/Yeast_Lu_2007_YMD.txt
./4932/Newman_et_al_yeast_data_SD.txt
./4932/Yeast_Lu_2007_YPD.txt
./4932/deGodoy_et_al_yeast_data.txt
./4932/Newman_et_al_yeast_data_YEPD.txt
./267671/controlMS1_Leptospira_Malmstroem_2009.txt
./267671/controlSpectral_Leptospira_Malmstroem_2009.txt'''

# datasets = [ f for f in os.listdir(folder) if isfile(join(folder,f)) ]
datasets = [f for f in files.split('\n')]

prev_species = None
ids_map = None  #re-use
for f in datasets:
    species_id = f.split('/')[1]
    print('processing', f)
    if not species_id == prev_species:
        ids_map = mapper.load_ids(species_id)
    mapper.add_string_internalids_column(species_id, join(folder, f), ids_map)
    shutil.move(join(folder, f) + '.out', '../output/v4.0/direct_mapping')
    prev_species = species_id

prev_species = None
ids_map = None  #re-use
for f in datasets:
    species_id = f.split("-")[0]
    print('processing', f)
    if not species_id == prev_species:
        ids_map = mapper.load_ids(species_id)
    mapper.add_string_internalids_column(species_id, join(folder, f), ids_map)
    prev_species = species_id
    
    

