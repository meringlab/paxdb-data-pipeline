#!/usr/bin/python
#
# author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
#

try:
    # python2:
    import ConfigParser
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

import os, yaml

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yml')) as f:
    configs = yaml.safe_load(f)
PAXDB_VERSION = configs['VERSION']['PAXDB']
with open(os.path.join(configs['FILE_PATHS']['PAXDB_INFO'], PAXDB_VERSION, 'species.yml')) as f:
    species_info = yaml.safe_load(f)
    
PROPERTIES = '/opt/paxdb/' + PAXDB_VERSION + '/pipeline.ini'

class PaxDbConfig():
    '''A class to hold all properties (better than a bunch of globals)'''
    SECTIONS = ['StringDb', 'postgresql', 'Google_account']

    def __init__(self, properties=PROPERTIES):
        '''param properties can either be a path, or file-like object'''
        cfg = self._parse_config(properties)
        self.paxdb_version = PAXDB_VERSION
        self.paxdb_version_sql = 'paxdb'+ '_'.join(PAXDB_VERSION.replace('v','').split('.'))
        self.google_user = cfg.get('Google_account', 'user')
        self.google_pass = cfg.get('Google_account', 'pass')
        self.spreadsheet_key = cfg.get('Google_account', 'spreadsheet_key')
        self.pg_url = 'host={0} port={1} user={2} dbname={3}'.format(
            cfg.get('postgresql', 'url'),
            cfg.get('postgresql', 'port'),
            cfg.get('postgresql', 'user'),
            'paxdb')
        self.string_db = 'string_' + cfg.get('StringDb', 'version')
        self.fasta_version = cfg.get('StringDb', 'fasta_version')
        self.SPECIES_IDs = list(species_info.keys())

    def _parse_config(self, properties):
        if isinstance(properties, str):
            cfg = self._parse_config_from_file(properties)
        else:
            cfg = self._parse_config_from_buffer(properties)

        if not _is_superset(cfg.sections(), self.SECTIONS):
            raise ValueError('some sections missing, expecting: {0}, got {1}'
                             .format(str(cfg.sections()), str(self.SECTIONS)))
        return cfg

    def _parse_config_from_buffer(self, properties):
        cfg = ConfigParser()
        cfg.readfp(properties)
        return cfg

    def _parse_config_from_file(self, properties):
        cfg = ConfigParser()
        files_read = cfg.read(properties)
        if len(files_read) == 0:
            raise ValueError('failed to read properties: ' + properties)
        return cfg


def _is_superset(sublist, superlist):
    # TODO check if they are lists
    if not (isinstance(sublist, list) and isinstance(superlist, list)):
        raise ValueError('expecting lists, got {0}, {1}'.format(type(sublist), type(superlist)))
    return set(sublist).issuperset(superlist)


if __name__ == "__main__":
    c = PaxDbConfig(open(PROPERTIES))
    assert (c.string_db is not None)
