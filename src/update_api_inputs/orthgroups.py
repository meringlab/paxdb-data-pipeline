### compute ortholog groups linking the species
import os, shutil, yaml, sys

config_file = '../paxdb/config.yml'

with open(config_file) as f:
    config = yaml.load(f, Loader= yaml.BaseLoader)
    PAXDB_VERSION = config['VERSION']['PAXDB']
    LEVEL_IDS = config['ORTHOLOG_LEVEL'] ## already pruned after cladogram.py
    species_ids = set(config['SPECIES_IDS'])
    ID_file = config['FILE_PATHS']['PROTEIN_ID']
    eggnog_dir = config['FILE_PATHS']['EGGNOG']
    ortholog_path = config['FILE_PATHS']['MAPPED_ORTHLOG']

output_dir = f'../version_update/{PAXDB_VERSION}/orthgroups'

group_species = {}
group_line_idx = {}
for f in os.listdir(eggnog_dir):
    ortholog_group = os.path.splitext(f)[0]
    group_species[ortholog_group] = set()
    group_line_idx[ortholog_group] = set()
    with open(os.path.join(eggnog_dir, f)) as fr:
        for i,l in enumerate(fr):
            spe_id = l.split('\t')[2]
            if spe_id in species_ids:
                group_species[ortholog_group].add(spe_id)
                group_line_idx[ortholog_group].add(i)

for tmp_dir in ['tmp','tmp2']:
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

if os.path.isdir(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(os.path.join(output_dir,'pruned'))

def generate_nog_protein_map(ortholog_file, wanted_protein_names, species_ids):
    
    ortholog_group_nogID_protein_map = {}
    for i,l in enumerate(ortholog_file):
        items =  l.strip().split('\t')
        ortholog_group = items[0]
        nog_id = items[1]
        protein_name = items[-1]
        species_id = protein_name.split('.')[0]
        if species_id in species_ids:
            if not ortholog_group in ortholog_group_nogID_protein_map:
                ortholog_group_nogID_protein_map[ortholog_group] = {}
            nogID_protein_map = ortholog_group_nogID_protein_map[ortholog_group]
            wanted_protein_names.add(protein_name)
            if nog_id in nogID_protein_map:
                nogID_protein_map[nog_id].append(protein_name)
            else:
                nogID_protein_map[nog_id] = [protein_name]
    return ortholog_group_nogID_protein_map, wanted_protein_names

### collect the protein names required for final mapping, so IDmapper object won't get too large.
wanted_protein_names = set()
for ortholog_group, species_set in group_species.items():
    
    if len(species_set) > 0:
        
        with open(f'{eggnog_dir}/{ortholog_group}.tsv') as fr:
            ortholog_group_nogID_protein_map, wanted_protein_names = generate_nog_protein_map(fr, wanted_protein_names, species_ids)
        with open(f'tmp/{ortholog_group}.txt','w') as fw:
            for nogID, protein_list in ortholog_group_nogID_protein_map[ortholog_group].items():
                print(nogID, ' '.join(protein_list), sep = '\t', file = fw)

covered_species = set()
for i in group_species.values():
    covered_species.update(i)
not_covered_species = species_ids - covered_species ## required from mapped species

ortholog_group_additional_nogID_protein_map = {}
for f in os.listdir(ortholog_path):
    species = f.split('.')[0]
    if not species in not_covered_species:
        continue
    with open(os.path.join(ortholog_path,f)) as fr:
        tmp, wanted_protein_names = generate_nog_protein_map(fr, wanted_protein_names, not_covered_species)
    
    print('missing species patched:', species, 'with', len(tmp), 'nog entries:', list(tmp.keys()))
    
    for ortholog_group, nog_protein_map in tmp.items():
        if not ortholog_group in ortholog_group_additional_nogID_protein_map:
            ortholog_group_additional_nogID_protein_map[ortholog_group] = {}

        for nogID, protein_list in nog_protein_map.items():
            if not nogID in ortholog_group_additional_nogID_protein_map[ortholog_group]:
                ortholog_group_additional_nogID_protein_map[ortholog_group][nogID] = protein_list
            else:
                ortholog_group_additional_nogID_protein_map[ortholog_group][nogID] += protein_list
        
IDmapper = {}
with open(ID_file) as f:
    for l in f:
        p_id, p_name = l.strip().split('\t')
        if p_name in wanted_protein_names:
            IDmapper[p_name] = p_id

with open(f'{output_dir}/all_wanted_proteins.txt','w') as f:
    for p_name in wanted_protein_names:
        p_id = IDmapper[p_name]
        print(p_name,p_id, sep ='\t', file = f)

for f in os.listdir('tmp'):
    if not f.endswith('txt'):
        continue
    ortholog_group = f.split('.')[0]

    if ortholog_group not in LEVEL_IDS:
        fw = open('{}/pruned/{}-orthologs.txt'.format(output_dir, ortholog_group),'w') 
    else:
        fw = open('{}/{}-orthologs.txt'.format(output_dir, ortholog_group),'w')

    with open(f'tmp/{f}') as fr:
        for l in fr:
            l_list = l.strip().split()
            nog_id = l_list[0]
            try:
                additional_list = ortholog_group_additional_nogID_protein_map[ortholog_group][nog_id]
            except KeyError:
                additional_list = []
            finally:
                print('\t'.join([nog_id] + [IDmapper[i] for i in l_list[1:]+additional_list]), file = fw)
    fw.close()

# shutil.rmtree('tmp')

