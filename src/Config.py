#!/usr/bin/python
#
# author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
#
PAXDB_VERSION='v3.1'
PROPERTIES='/opt/paxdb/' + PAXDB_VERSION + '/pipeline.ini'

PAXDB_STRINGDB_MAPPING = { 'v3.1': '10_0',
                           'v3.0': '9_0',
                           'v2.1': '9_0',
                           'v2.0': '9_0',
                           'v1.0': '8_3'}

#SPECIES_IDS=[1148, 3702, 4896, 4932, 6239, 7227, 7460, 7955, 8364, 9031, 9606, 9615, 9823, 9913, 10090, 10116, 39947, 64091, 83332, 99287, 160490, 198214, 224308, 267671, 449447, 511145, 546414, 593117] # no SC for 722438

from ConfigParser import ConfigParser

class PaxDbConfig():
    '''A class to hold all properties (better than a bunch of globals)'''
    SECTIONS=['StringDb', 'postgresql', 'Google_account']

    def __init__(self, properties = PROPERTIES):
        '''param properties can either be a path, or file-like object'''
        config = self._parse_config(properties)
        self.paxdb_version = PAXDB_VERSION
        self.google_user = config.get('Google_account','user')
        self.google_pass = config.get('Google_account','pass')
        self.pg_url = 'host={0} port={1} user={2} dbname={3}'.format(
            config.get('postgresql','url'),
            config.get('postgresql','port'),
            config.get('postgresql','user'),
            'string_' + config.get('StringDb','version'))
        self.string_db='string_' + config.get('StringDb','version')
        self.fasta_version=config.get('StringDb','fasta_version')

    def _parse_config(self, properties):
        if isinstance(properties, str):
            config = self._parse_config_from_file(properties) 
        else:
            config = self._parse_config_from_buffer(properties)

        if not _is_superset(config.sections(), self.SECTIONS):
            raise ValueError('some sections missing, expecting: {0}, got {1}'
                             .format(str(config.sections()),str(self.SECTIONS)))
        
        if PAXDB_STRINGDB_MAPPING[PAXDB_VERSION] != config.get('StringDb','version'):
            raise ValueError('paxdb <-> stringdb version mismatch {0} <-> {1}'.format(PAXDB_VERSION, config.get('StringDb','version')))

        return config

    def _parse_config_from_buffer(self, properties):
        config=ConfigParser()
        config.readfp(properties)
        return config

    def _parse_config_from_file(self, properties):
        config=ConfigParser()
        files_read = config.read(properties)
        if len(files_read) == 0:
            raise ValueError('failed to read properties: ' + properties)
        return config
        
        
def _is_superset(sublist, superlist):
    # TODO check if they are lists
    if not (isinstance(sublist, list) and isinstance(superlist, list)):
        raise ValueError('expecting lists, got {0}, {1}'.format(type(sublist),type(superlist)))
    return set(sublist).issuperset(superlist)

if __name__ == "__main__":
    c = PaxDbConfig(open(PROPERTIES))
    assert(c.string_db is not None)
