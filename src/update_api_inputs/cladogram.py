### construct cladogram from 
### - species
### - linked upper taxonomic levels (generated from eggnog 5 ortholog files of the species)
### - current ncbi node tree

import yaml
config_file = '../paxdb/config.yml'

with open(config_file) as f:
    config = yaml.safe_load(f)
    
tree_file = config['FILE_PATHS']['TAXON_NODES']
species_ids = config['SPECIES_IDS']
taxon_ids = config['ORTHOLOG_LEVEL']
total_ids = taxon_ids + species_ids

child_parent = {}
with open(tree_file) as f:
    for l in f:
        c = l.split('|')[0].strip()
        p = l.split('|')[1].strip()
        child_parent[c] = p

lineages = {}
for i in species_ids:
    lineages[i] = [i]
    j=i
    while j != '1':
        j = child_parent[j]
        if j in total_ids:
            lineages[i].append(j)

rev_lineages = [l[::-1] for l in lineages.values()]

draft_tree = {}
for l in rev_lineages:
    current_node = draft_tree
    for node in l:
        if not node in current_node:
            if len(current_node) > 0 and node not in current_node:
                    current_node[node] = {}
                
            else:
                current_node[node] = {}
        current_node = current_node[node]

def remove_excess_child_node(d):
    new_d = {}
    for k, v in d.items():
        if len(v) == 1:
            new_d.update(remove_excess_child_node(v))
        else:
            new_d[k] = remove_excess_child_node(v)
    return new_d

final_tree = remove_excess_child_node(draft_tree)

def get_middle_node(d):
    for k,v in d.items():
        if len(v)!=0:
            yield k
            yield from get_middle_node(v)
        
final_remain_taxon_level = [i for i in get_middle_node(final_tree)]

### update ortholog_level or write if not present
with open(config_file,'r') as f:
    config = yaml.safe_load(f)
    config['ORTHOLOG_LEVEL'] = final_remain_taxon_level

if config:
    with open(config_file,'w') as f:
        yaml.safe_dump(config, f)