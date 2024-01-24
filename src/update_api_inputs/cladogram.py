### construct cladogram from 
### - species
### - linked upper taxonomic levels (generated from eggnog 5 ortholog files of the species)
### - current ncbi node tree

import yaml, copy, sys, argparse, json

config_file = '../paxdb/config.yml'
version = 'v5.0'
config_arv = f'../paxdb/arv/config_{version}.yml'

with open(config_file) as f:
    config = yaml.safe_load(f)
 
tree_file = config['FILE_PATHS']['TAXON_NODES']
species_ids = [str(i) for i in config['SPECIES_IDS']]
taxon_ids = [str(i) for i in config['ORTHOLOG_LEVEL']]

def remove_excess_child_node(d, exception = set()): ## exception is set of nodes to keep
        new_d = {}
        for k, v in d.items():
            if exception and k in exception:
                new_d[k] = remove_excess_child_node(v, exception)
            elif len(v) == 1:
                new_d.update(remove_excess_child_node(v, exception))
            else:
                new_d[k] = remove_excess_child_node(v, exception)
        return new_d
    
    
def get_middle_node(d):
    for k,v in d.items():
        if len(v)!=0:
            yield k
            yield from get_middle_node(v)
            
def recursive_change_name(d, name_map, new_d):
    new_d = copy.deepcopy(d)
    
    for k in d.keys():
        
        new_k = name_map[k]
        new_d[new_k] = new_d[k]
        del new_d[k]
        
        new_d[new_k] = recursive_change_name(d[k], name_map, new_d[new_k])
        
    return new_d  
      
if __name__ == '__main__':
    ## added_nodes for UI to list specific nodes (which doesn't change config file ORTHOLOGY_LEVEL)
    ## Orthology API would prefer nodes with at least 3 species and remove large nodes, when not at kingdom/phylum level
    ## UI wants rather interesting model species
    # example: python3 cladogram.py -a 28211,8292,7898,9612 -e 9612
    parser = argparse.ArgumentParser(
                    prog = 'Cladogram',
                    description = 'Creates cladogram given taxon nodes and species IDs from paxdb config')
    parser.add_argument('-e', '--nodeException', default='') 
    parser.add_argument('-a', '--addedNodes', default='') 
    args = parser.parse_args()
    if args.addedNodes:
        addedNodes = args.addedNodes.split(',')
    else:
        addedNodes = []
    if args.nodeException:
        nodeException = set(args.nodeException.split(','))
    else:
        nodeException = set()
        
    print('nodeException:', nodeException)
    print('addedNodes:', addedNodes)
    # sys.exit()
    
    ## 1. update ortholog level 
    ### WARNING: rewrites the config file, save the previous version in arv/
    
    total_ids = taxon_ids + species_ids + addedNodes
    
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

    final_tree = remove_excess_child_node(draft_tree, nodeException)

    final_remain_taxon_level = [i for i in get_middle_node(final_tree)]

    ### update ortholog_level or write if not present
    with open(config_file,'r') as f:
        config = yaml.safe_load(f)
        
    if config and addedNodes == []:
        with open(config_arv,'w') as f:
            yaml.safe_dump(config, f)
            
        config['ORTHOLOG_LEVEL'] = [int(i) for i in final_remain_taxon_level]
        with open(config_file,'w') as f:
            yaml.safe_dump(config, f)
        
    ## 2. write cladogram in pretty print for reading
    from pprint import pprint

    name_file = config['FILE_PATHS']['ORTHOLOG_LEVEL']
    new_species_file = f'../version_update/{version}/new_species.yml'
    with open(new_species_file) as f:
        new_species = yaml.safe_load(f)
    new_species_set = set([str(sp) for sp in new_species])
    
    cladogram_file = f'../version_update/{version}/cladogram.json'
    with open(cladogram_file, 'w') as wf:
        json.dump(final_tree, fp=wf, indent = 4)
        
    cladogram_file = f'../version_update/{version}/cladogram-shortname.json'
    names_map = {}
    with open(name_file) as f:
        for l in f:
            content = l.split('|')
            if content[-2].strip() == 'scientific name':
                sp_id = content[0].strip()
                name = content[1].strip()
                shortname = ' '.join(name.split()[:2])
                names_map[sp_id] = shortname
                
    named_final_tree = recursive_change_name(final_tree, names_map, {})
    with open(cladogram_file, 'w') as wf:
        json.dump(named_final_tree, fp=wf, indent = 4)

    cladogram_file = f'../version_update/{version}/cladogram-named.txt'

    names_map = {}
    with open(name_file) as f:
        for l in f:
            content = l.split('|')
            if content[-2].strip() == 'scientific name':
                sp_id = content[0].strip()
                if sp_id in new_species_set:
                    names_map[sp_id] = sp_id+'-NEW-' + content[1].strip()
                else:
                    names_map[sp_id] = sp_id+'-' + content[1].strip()
    

    named_final_tree = recursive_change_name(final_tree, names_map, {})
    with open(cladogram_file, 'w') as wf:
        # pprint(named_final_tree, stream=wf)
        json.dump(named_final_tree, fp=wf, indent = 4)
    
    ### further regex to remove ": {}" for each line