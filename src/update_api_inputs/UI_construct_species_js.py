### construct species.js ###
### created 2021-11-30 by Qingyao

### output export default {xxx (species_id)}
### species_id: {id, name, compact_name, num_proteins, genome_source, genome_source_version, datasets: [],
### total_coverage, average_coverage, topProteins:[]}
### datasets: [{id, name, score, weight, description, organ, integrated, coverage, publication_year, num_abundance, hasPeptideCounts, filename},]
### topProteins: [{id, external_id, abundance, rank, name, annotation}]

### used input files
### abundances/ folder (paxdb-api)
### eggnog5_genome_linkout.txt (paxdb-api)
### postgresql paxdb4_2

import os, json, re
import psycopg2

paxdb_version = 'paxdb5_0'
version_no = 'v5.0'

abundance_dir = f'../../output/{version_no}/final/'
eggnog_file = f'../version_update/{version_no}/eggnog5_genome_linkout.txt'

datasets_fields = set(['id', 'name', 'score', 'weight', 'description', 'organ', 'integrated', 'coverage', 'publication_year', 'num_abundance', 'link','hasPeptideCounts'])
image_credit_info = {
    73239: 'Image credit to Tamasa Araki, Hirotaka Kobayashi and Takeshi Annoura at National Institute of Infectious Diseases (NIID), Tokyo, Japan',
    224326: 'Image credit to Marie Vancova and Natasha Rudenko at Biology Centre CAS, Institute of Parasitology, Czechia',
    5476: "Image from Fig 5B Polonelli et al., A Naturally Occuring Antibody Fragment... 2016 Scientific Reports",
    65489: "Adapted from Fig 1, Wambugu et al., Conservation and utilization of African... 2013 Rice (N Y)",
    5811: "Adapted from Fig 6A Almutairi et al., Exploring the Antiparasitic Activity of... 2022 Molecules",
    272620: "Adapted from Fig 7, Cheng et al., Klebsiella pneumoniae infection causes... 2021 Vet Res.",
    347256: "Adapted from Fig 1f, Xiang et al., Infection due to Mycoplasma hominis... 2019 BMC Infect Dis.",
    55529: "Adapted from Fig 1, Zauner et al., A Re-Evaluation of the Nucleomorph... 2019 Genome Biol Evol.",
    187420: "Adapted from Fig 5, Liu et al., Comparative proteomic analysis of Methanothermobacter... 2019 Microbiologyopen.",
    572546: "Adapted from Fig 2, von Jan et al, Complete genome sequence of Archaeoglobus ... 2010 Stand Genomic Sci.",
    589924: "Image by D. Rose published in: Hafenbradl et al, 1996 Arch. Microbiol.",
}

final_json = {}

### 1. go through datasets
print('step 1')
for file_name in os.listdir(abundance_dir):
    species_id = int(file_name.split('-')[0])
    if not species_id in final_json:
        final_json[species_id] = {'id': species_id, 'datasets':[]}
    final_json[species_id]['datasets'].append({'filename': file_name})
    with open(os.path.join(abundance_dir, file_name)) as f:
        count = 0
        for l in f:
            if l.startswith('#'):
                try:
                    field, val = l.strip().split(': ')
                except ValueError:
                    n_col = len(l.strip().split())
                    if n_col != 1: ## empty line
                        if n_col == 4:
                            final_json[species_id]['datasets'][-1]['hasPeptideCounts'] = True
                        elif n_col == 3:
                            final_json[species_id]['datasets'][-1]['hasPeptideCounts'] = False
                    continue

                field = field[1:]
                if field in datasets_fields:
                    if field in set(['id','coverage','publication_year']):
                        final_json[species_id]['datasets'][-1][field] = int(val)
                    elif field == 'score':
                        final_json[species_id]['datasets'][-1][field] = float(val)
                    elif field == 'integrated':
                        final_json[species_id]['datasets'][-1][field] = val == 'true'
                    elif field == 'organ':
                        final_json[species_id]['datasets'][-1][field] = val
                        final_json[species_id]['datasets'][-1]['organ_show'] = val.replace('_',' ').capitalize()
                    else:
                        final_json[species_id]['datasets'][-1][field] = val
            else:
                count+=1
        
        final_json[species_id]['datasets'][-1]['num_abundances'] = count


### 2. add genome links
print('step 2')
with open(eggnog_file) as f:
    for l in f:
        values = l.split('\t')
        species_id = int(values[1])
        source_type = values[2]
        genome_source_version = values[3].strip()
        if source_type == '':
            source_type = 'NCBI Taxonomy'
        source_link = values[4]
        genome_source = f"<a href='{source_link}'>{source_type}</a>"
        if species_id in final_json:
            final_json[species_id]['genome_source'] = genome_source
            final_json[species_id]['genome_source_version'] = genome_source_version
        else:
            print(species_id)

### 3. on species-level, fetch info from sql, and compute overall abundance
print('step 3')
conn = psycopg2.connect(
        host='imlslnx-atlas.uzh.ch',
        dbname='paxdb',
        user='postgres',
        port = '5432'
    )
cur = conn.cursor()

def getTopProteins(file_path):
    topProteins = []
    ## get file with internal ID column
    file_name = os.path.basename(file_path)
    species_id = file_name.split('-')[0]
    file_path = os.path.join('../../output/', version_no, species_id, file_name)
    if not os.path.isfile(file_path):
        file_path = os.path.join('../../output/', version_no, species_id, file_name.replace(species_id+'-',''))
    if not os.path.isfile(file_path):
        file_path = os.path.join('../../output/', version_no, species_id, file_name.replace(species_id+'-',species_id + '_'))
    with open(file_path) as f:
        rank = 0
        for l in f:
            if not l.startswith('#'):
                
                internal_id, external_id, abundance = l.strip().split()[:3]
                cur.execute(f'select preferred_name, annotation from {paxdb_version}.proteins where protein_id = {internal_id}')
                name, annotation = cur.fetchone()
                topProteins.append({'id': int(internal_id),
                                    'ext_id': external_id,
                                    'abundance': int(abundance),
                                    'rank': rank,
                                    'name': name,
                                    'annotation': annotation
                                })
                rank+=1
                if rank == 8:
                    break
    return topProteins

def getProteins(file_path):
    proteins = []
    with open(file_path) as f:
        for l in f:
            if not l.startswith('#'):
                proteins.append(l.strip().split()[0])
    return proteins

for species, info in final_json.items():
    
    cur.execute(f'select official_name, compact_name, num_proteins from {paxdb_version}.species where species_id = {species}')
    res = cur.fetchone()
    info['name']=res[0]
    info['compact_name'] = res[1]
    info['num_proteins'] = res[2]
    # print(species)
    ds = info['datasets']
    if len(ds) == 1:
        
        info['total_coverage'] = ds[0]['coverage']
        info['average_coverage'] = ds[0]['coverage']
        info['topProteins'] = getTopProteins(os.path.join(abundance_dir, ds[0]['filename']))
    else:
        average_coverage = 0
        all_proteins = set()
        topProteins = []
        for d in ds:
            average_coverage+=d['coverage']
            all_proteins.update(getProteins(os.path.join(abundance_dir, d['filename'])))
            if d['filename'].endswith('WHOLE_ORGANISM-integrated.txt'):
                topProteins = getTopProteins(os.path.join(abundance_dir, d['filename']))
            
        average_coverage /= len(ds)
        total_coverage = len(all_proteins)/info['num_proteins']
        info['total_coverage'] = round(total_coverage*100)
        info['average_coverage'] = round(average_coverage)
        if len(topProteins) == 0: ## there's no whole organism, then get the top from organ-level integrated file and re-rank them.
            for d in ds:
                max_coverage = 0
                max_sum_coverage_score = 0
                if d['filename'].endswith('integrated.txt'):
                    if d['coverage'] > max_coverage:
                        topProteins = getTopProteins(os.path.join(abundance_dir, d['filename']))
                        max_coverage = d['coverage']
                        max_sum_coverage_score = d['coverage'] * d['score']
                    if d['coverage'] == max_coverage:
                        if d['coverage'] * d['score'] > max_sum_coverage_score:
                            topProteins = getTopProteins(os.path.join(abundance_dir, d['filename']))
                            max_sum_coverage_score = d['coverage'] * d['score']
            if len(topProteins) == 0: ## no integrated data but individual datasets
                max_coverage = 0
                max_sum_coverage_score = 0
                for d in ds:
                    if d['coverage'] > max_coverage:
                        topProteins = getTopProteins(os.path.join(abundance_dir, d['filename']))
                        max_coverage = d['coverage']
                        max_sum_coverage_score = d['coverage'] * d['score']
                    if d['coverage'] == max_coverage:
                        if d['coverage'] * d['score'] > max_sum_coverage_score:
                            topProteins = getTopProteins(os.path.join(abundance_dir, d['filename']))
                            max_sum_coverage_score = d['coverage'] * d['score']
            
        info['topProteins'] = topProteins

### 4. add image credit
for species_id, info in final_json.items():
    if species_id in image_credit_info:
        info['image_credit'] = image_credit_info[species_id]
    # else:
    #     info['image_credit'] = ''

with open(f'../version_update/{version_no}/species_for_js.json', 'w') as wf:
    wf.write(re.sub(r'"(.*?)"(?=:)', r'\1', json.dumps(final_json, indent='  ')))

# with open(f'../version_update/{version_no}/species.json', 'w') as wf:
#     wf.write(json.dumps(final_json))