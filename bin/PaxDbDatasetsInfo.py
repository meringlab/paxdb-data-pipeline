#!/usr/bin/python
# 
# A set of classes to fetch "PaxDB data information" google doc. 
# 
PROPERTIES='/opt/paxdb/v3.1/pipeline.ini'
SPREADSHEET_KEY='0AkvR36gTdQzedFYwenAxMFY3NENJeDRHeWU4TG9IYXc'

import sys
sys.path.append('./gspread')
import gspread
import ConfigParser

class DatasetInfo():
    def __init__(self, columns, row):
        self.species_id = int(row[0])
        self.species_name = row[columns.index('species')]
        self.dataset = row[columns.index('dataset')]
        self.score = None
        if row[columns.index('score')]:
            self.score = float(row[columns.index('score')])
        try:
            self.weight = float(row[columns.index('weight')])
        except ValueError:
            self.weight = None            
#        self.num_abundances = int(row[columns.index('protein_number')]) # todo read from abundance files
        self.genome_size = int(row[columns.index('genome_size')])
        self.organ = row[columns.index('organ')].upper()  # if ValueError raised set to None or 'WHOLE'
        self.integrated = False
        if row[columns.index('integrated')] == 'Y':
            self.integrated = True
        self.publication = _n_to_None(row[columns.index('publication/source')])
        self.source_link = _n_to_None(row[columns.index('source_link')])
        self.condition_media = _n_to_None(row[columns.index('condition/media')])
        self.quantification_method = _n_to_None(row[columns.index('quantification_method')]) or 'Spectral counting'

    def __str__(self):
        import json
        return json.dumps(self.__dict__)
    def __repr__(self):
        return "Dataset(species: {0}, organ: {1}, dataset: {2})".format(self.species_id, self.organ, self.dataset)

def _n_to_None(value):
    return None if 'N' == value else value

class PaxDbDatasetsInfo():
    def __init__(self, properties=PROPERTIES, google_doc_key=SPREADSHEET_KEY, whole_organism_sheet=None, tissues_sheet=None):
        self._set_auth_props(properties)
        self._load_data(google_doc_key, whole_organism_sheet, tissues_sheet)

    def _set_auth_props(self, properties_file):
        config=ConfigParser.ConfigParser()
        config.read(properties_file)
        self._google_user = config.get('Google_account','user')
        self._google_pass = config.get('Google_account','pass')

    def _load_data(self, google_doc_key, whole_organism_sheet, tissues_sheet):
        #gc = gspread.Client(auth=None) # doesn't work, but this does:
        gclient = gspread.login(self._google_user, self._google_pass)
        doc = gclient.open_by_key(google_doc_key)
        self.datasets = dict()
        for ds in (_load_datasets(_open_sheet(doc, whole_organism_sheet or 0)) + 
                   _load_datasets(_open_sheet(doc, tissues_sheet or 1))):
            organ = ds.organ
            species = str(ds.species_id)
            if not self.datasets.has_key(species):
                self.datasets[species] = dict()
            by_organ = self.datasets[species]
            if not by_organ.has_key(organ):
                by_organ[organ] = []
            by_organ[organ].append(ds)

def _load_datasets(sheet):
    matrix = sheet.get_all_values()
    column_names= map((lambda c: c.strip() if isinstance(c, str) else c), matrix[0])
    # get_all_values() returns '' for empty cells, so convert to None:
    column_names= map((lambda c: None if c =='' else c), column_names) 
    non_empty_rows = filter((lambda r: not not r), matrix[1:])
    datasets = map((lambda row: DatasetInfo(column_names, row)), non_empty_rows)
    return datasets

def _open_sheet(doc, sheet):
    return doc.worksheet(sheet) if isinstance(sheet, str) else doc.get_worksheet(sheet)

if __name__ == "__main__":
    info = PaxDbDatasetsInfo()
    d = info.whole_organ_datasets[0]
    print d.species, d.dataset
