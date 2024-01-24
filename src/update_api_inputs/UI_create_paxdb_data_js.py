### construct species_id to synonyms mapping for front-end 

from collections import defaultdict
import yaml, json, os, argparse
import subprocess as sbp

config_file = '../paxdb/config.yml'

with open(config_file) as f:
    config = yaml.safe_load(f)

paxdb_version = config['VERSION']['PAXDB']
eggnog_version = config['VERSION']['EGGNOG']
string_version = config['VERSION']['STRING']

name_file = config['FILE_PATHS']['ORTHOLOG_LEVEL']
species_file = f'/mnt/mnemo6/damian/STRING_derived_{string_version}/download_files/species.{string_version}.txt'

species_ids = set([str(i) for i in config['SPECIES_IDS']])
out_dir = f'../version_update/{paxdb_version}/UI_files'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                    prog = 'UI_utility_',
                    description = 'Creates cladogram given taxon nodes and species IDs from paxdb config')
    parser.add_argument('-s', '--steps', default='1,2,3,4', help = 'which step to run? default ALL') 
    parser.add_argument('-e', '--nodeException', default='', help = 'In step 4 to generate cladogram: which intermediate node to include') 
    args = parser.parse_args()
    if args.nodeException: 
        nodeException = set(args.nodeException.split(',')) 
    else:
        nodeException = set()
        
    steps = set(args.steps.split(','))
    print('nodeException:', nodeException)
    print('steps:', steps)
    
    ### SPECIES_SYNONYMS
    if '1' in steps:
        out_file = os.path.join(out_dir, 'species_synonym_map.out')

        names_map = defaultdict(set)
        with open(name_file) as f:
            for l in f:
                content = l.split('|')
                sp_id = content[0].strip()
                if sp_id in species_ids and content[-2].strip() not in ['type material', 'misspelling', 'authority']:
                    names_map[sp_id].add(content[1].strip().replace('"',''))

        with open(out_file, 'w') as f: 
            for sp_id, names in names_map.items():
                for name in names:
                    if ' ' in name or '-' in name:
                        print('"' + name + '": "' + sp_id + '",', file = f)
                    else:
                        print(name + ': "' + sp_id + '",', file = f)
                        
        sbp.run(f'sort {out_file} > \
            {out_dir}/species_synonym_map.out_sorted', shell = True)

    ## SPECIES_SHORT_NAMES
    if '2' in steps:
        in_file = os.path.join(out_dir, os.pardir, 'species.yml')
        with open(in_file) as f:
            species_dict = yaml.load(f, Loader = yaml.SafeLoader)

        for i, j in species_dict.items():
            name = j[:2] + ' ' + j[2:]
            if len(name) > 15:
                species_dict[i] = ' '.join(name.split(' ')[:2])
            else:
                species_dict[i] = name

        out_file = os.path.join(out_dir, 'species_short_names.json')
        with open(out_file, 'w') as wf:
            json.dump(species_dict, fp = wf, indent=2)

    ## SPECIES_FULL_NAMES: unsorted dict or sorted list
    if '3' in steps:
        ## SPECIES_FULL_NAMES
        species_fullname = {}
        with open(species_file) as f:
            next(f)
            for l in f:
                taxonid =  l.split('\t')[0]
                if taxonid in species_ids:
                    name = l.split('\t')[3]
                    species_fullname[int(taxonid)] = name
                    
        out_file = os.path.join(out_dir, 'species_full_names.json')
        with open(out_file, 'w') as wf:
            json.dump(species_fullname, fp = wf, indent=2)


        ## SPECIES_FULL_NAMES_SORTED
        ## first 3 stays
        first3 = [9606, 4932, 511145]
        species_fullname_list = [{'id': i, 'official_name': j} for i, j in species_fullname.items()]
        species_fullname_list.sort(key= lambda x: x['official_name'])
        for species_id in reversed(first3):

            item = list(filter(lambda x: x['id']==species_id,species_fullname_list))[0]
            species_fullname_list.remove(item)
            species_fullname_list.insert(0,item)
            
        out_file = os.path.join(out_dir, 'species_full_names_sorted.json')
        with open(out_file, 'w') as wf:
            json.dump(species_fullname_list, fp = wf, indent=2)
        
    ## CLADOGRAM
    ## run cladogram.py with added nodes 28211, 8292, 7898, 9612 (wolf species -> parent of dog subspecies)
    if '4' in steps:
        required_nodes = {
            1:'Cellular Organisms',
            2: 'Bacteria',
            1117: 'Cyanobacteria',
            1239: 'Firmicutes',
            201174: 'Actinobacteria',
            203691: 'Spirochaetes',
            200940: 'Thermodesulfobacteria',
            544448: 'Tenericutes',
            68336: 'Bacteroidetes',
            1224: 'Proteobacteria',
            28211: 'Alphaproteobacteria',
            1236: 'Gammaproteobacteria',
            2157: 'Archaea',
            2759: 'Eukaryotes',
            5794: 'Apicomplexa',
            5653: 'Kinetoplasts',
            4751: 'Fungi',
            35493: 'Plants',
            33208: 'Animals',
            # 6656: 'Arthropods',
            7711: 'Vertebrates',
            40674: 'Mammals',
            8292: 'Amphibians',
            7898: 'Fish'
        }
        
        others = {
            'Other bacteria': [2, 1239,1117, 201174, 203691, 200940, 544448, 68336, 1224],
            'Other proteobacteria':[1224, 1236, 28211],
            'Invertebrates': [33208, 7711],
            'Other eukaryotes': [2759, 5794, 5653, 4751, 35493, 33208]
        }


        def get_all_children(d, nodeException = set()): #nodeException is a set of node to keep
            for k,v in d.items():
                if len(v) == 0 or k.split('-')[0] in nodeException:
                    yield k.split('-')[0]
                yield from get_all_children(v, nodeException)

        # print(list(get_all_children({'a':{'b':{},'c':{}}, 'd':{}})))
        in_file = os.path.join(out_dir,os.pardir,'cladogram-named.txt')
        with open(in_file) as f:
            cladogram = json.load(f)


        def update_dict(d, nodeException = set(), dict_nodes_children = dict()):
            for k,v in d.items():
                node_id = int(k.split('-')[0])
                if node_id in required_nodes:
                    dict_nodes_children[required_nodes[node_id]] = list(get_all_children(v, nodeException))
                update_dict(v, nodeException, dict_nodes_children)
            return dict_nodes_children

        # print(update_dict({'1-a':{'2-b':{},'3-c':{}}, '4-d':{}}))

        dict_nodes_children = update_dict(cladogram, nodeException)
        
        for other_category, node_subtraction in others.items():
            all = set(dict_nodes_children[required_nodes[node_subtraction[0]]])
            for rm_id in range(1, len(node_subtraction)):
                all -= set(dict_nodes_children[required_nodes[node_subtraction[rm_id]]])
            dict_nodes_children[other_category] = list(all)
            
        out_file = os.path.join(out_dir, 'cladogram.txt')
        with open(out_file, 'w') as wf:
            json.dump(dict_nodes_children, fp = wf, indent = 2)
                
        print('\n'.join([k+ ' (' + str(len(v)) + ')' for k,v in dict_nodes_children.items()]))