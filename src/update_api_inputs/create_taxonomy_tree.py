### construct taxonomy_tree.tsv for orhtology-lib from 
### - species
### - linked upper taxonomic levels (generated from eggnog 5 ortholog files of the species)
### - current ncbi node tree

import yaml, sys
from datetime import datetime
config_file = '../paxdb/config.yml'

with open(config_file) as f:
    config = yaml.safe_load(f)
    
tree_file = config['FILE_PATHS']['TAXON_NODES']
name_file = config['FILE_PATHS']['ORTHOLOG_LEVEL']
species_ids = set([str(i) for i in config['SPECIES_IDS']])
taxon_ids = set([str(i) for i in config['ORTHOLOG_LEVEL']])
total_ids = taxon_ids | species_ids

output_file = f"../version_update/{config['VERSION']['PAXDB']}/taxonomy_tree.tsv"

child_parent = {}
with open(tree_file) as f:
    for l in f:
        c = l.split('|')[0].strip()
        p = l.split('|')[1].strip()
        child_parent[c] = p

names_map = {}
with open(name_file) as f:
    for l in f:
        content = l.split('|')
        if content[-2].strip() == 'scientific name':
            names_map[content[0].strip()] = content[1].strip()

def get_name(node):
    if node == '1':
        return 'luca'
    else:
        return names_map[node]

def get_upper_tree_node(node):
    p = child_parent[node]
    if p in taxon_ids:
        return p
    else:
        return get_upper_tree_node(p)

with open(output_file, 'w') as f:
    print(f'## created: {datetime.now().isoformat()}', file = f)
    print('## script: /mnt/mnemo6/qingyao/paxDB/data-pipeline/src/update_api_inputs/create_taxonomy_tree.py', file = f)
    
    for i in total_ids:
        p = get_upper_tree_node(i)
        if i == p:
            continue
        print(i, p, get_name(i), get_name(p).lower(), sep = '\t', file = f)        
