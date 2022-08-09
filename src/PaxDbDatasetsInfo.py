#!/usr/bin/python
# 
# A set of classes to fetch "PaxDB data information" google doc. 
#
import os
from os.path import join
from oauth2client.service_account import ServiceAccountCredentials

from paxdb.config import PaxDbConfig

cfg = PaxDbConfig()

PROPERTIES = '/opt/paxdb/' + cfg.paxdb_version + '/pipeline.ini'

import sys

sys.path.append('./gspread')
import gspread


class DatasetInfo():
    def __init__(self, columns, row):
        # self.dataset_id = int(row[0])
        self.species_id = row[columns.index('taxid')].strip()
        self.species_name = row[columns.index('species')].strip()
        self.dataset = row[columns.index('dataset')].strip()
        
        try:
            self.score = float(row[columns.index('score')])
        except ValueError:
            self.score = None

        try:
            self.weight = float(row[columns.index('weight')])
        except ValueError:
            self.weight = None
        # self.num_abundances = int(row[columns.index('protein_number')]) # todo read from abundance files
        try:
            self.genome_size = int(row[columns.index('genome_size')])
        except:
            self.genome_size = -1
        self.organ = row[columns.index('organ')].upper()  # if ValueError raised set to None or 'WHOLE'

        if row[columns.index('integrated')] == 'Y':
            self.integrated = True
        else:
            self.integrated = False
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
    def __init__(self, google_doc_key=cfg.spreadsheet_key, whole_organism_sheet=None, tissues_sheet=None, integrated_sheet=None):
        self._load_data(google_doc_key, whole_organism_sheet, tissues_sheet, integrated_sheet)

    def get_dataset_info(self, species_id, dataset_name):
        by_organ = self.datasets[species_id]
        for organ in by_organ:
            for d in by_organ[organ]:
                if dataset_name == os.path.splitext(d.dataset)[0]:
                    return d
        raise ValueError("no dataset info for %s", dataset_name)
    
    # def get_dataset_number(self): ## assigned dataset_id
    #     return self.datasets_last_number

    def _load_data(self, google_doc_key, whole_organism_sheet, tissues_sheet, integrated_sheet):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(join('/opt/paxdb/', cfg.paxdb_version, 'google-api-key.json'), scope)
        gclient = gspread.authorize(credentials)

        doc = gclient.open_by_key(google_doc_key)
        self.datasets = dict()
        
        ds_whole = _load_datasets(_open_sheet(doc, whole_organism_sheet or 0))
        ds_tissue = _load_datasets(_open_sheet(doc, tissues_sheet or 1))
        ds_integrated = _load_datasets(_open_sheet(doc, integrated_sheet or 2))

        for ds in (ds_whole + ds_tissue + ds_integrated):
            organ = ds.organ
            species = str(ds.species_id)
            if not species in self.datasets:
                self.datasets[species] = dict()
            by_organ = self.datasets[species]
            if not organ in by_organ:
                by_organ[organ] = []
            by_organ[organ].append(ds)
        

def _load_datasets(sheet):
    matrix = sheet.get_all_values()
    column_names = map((lambda c: c.strip() if isinstance(c, str) else c), matrix[0])
    # get_all_values() returns '' for empty cells, so convert to None:
    column_names = list(map((lambda c: None if c == '' else c), column_names))
    non_empty_rows = list(filter((lambda r: not not r), matrix[1:]))
    datasets = list(map((lambda row: DatasetInfo(column_names, row)), non_empty_rows))
    return datasets


def _open_sheet(doc, sheet):
    return doc.worksheet(sheet) if isinstance(sheet, str) else doc.get_worksheet(sheet)


if __name__ == "__main__":
    info = PaxDbDatasetsInfo()
    d = info.datasets['1148']['WHOLE_ORGANISM'][0]
    print(d.species, d.dataset)
