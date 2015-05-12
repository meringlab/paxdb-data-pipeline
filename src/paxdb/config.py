#!/usr/bin/python
#
# author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
#
PAXDB_VERSION = 'v4.0'
PROPERTIES = '/opt/paxdb/' + PAXDB_VERSION + '/pipeline.ini'

PAXDB_STRINGDB_MAPPING = {'v4.0': '10_0',
                          'v3.0': '9_0',
                          'v2.1': '9_0',
                          'v2.0': '9_0',
                          'v1.0': '8_3'}

SPECIES_IDS = [882, 1148, 3055, 3702, 4081, 4577, 4896, 4932, 5061, 5691, 5821, 5833, 6239, 7165, 7227, 7460, 7955, 8364,
               9031, 9598, 9606, 9615, 9796, 9823, 9913, 10090, 10116, 39947, 44689, 64091, 83332, 85962, 99287, 122586,
               158878, 160490, 169963, 192222, 198214, 208964, 211586, 214092, 214684, 224308, 226186, 243159, 260799,
               267671, 272623, 272624, 283166, 352914, 353153, 449447, 511145, 546414, 593117, 722438]

try:
    # python2:
    import ConfigParser
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


class PaxDbConfig():
    '''A class to hold all properties (better than a bunch of globals)'''
    SECTIONS = ['StringDb', 'postgresql', 'Google_account']

    def __init__(self, properties=PROPERTIES):
        '''param properties can either be a path, or file-like object'''
        cfg = self._parse_config(properties)
        self.paxdb_version = PAXDB_VERSION
        self.google_user = cfg.get('Google_account', 'user')
        self.google_pass = cfg.get('Google_account', 'pass')
        self.spreadsheet_key = cfg.get('Google_account', 'spreadsheet_key')
        self.pg_url = 'host={0} port={1} user={2} dbname={3}'.format(
            cfg.get('postgresql', 'url'),
            cfg.get('postgresql', 'port'),
            cfg.get('postgresql', 'user'),
            'string_' + cfg.get('StringDb', 'version'))
        self.string_db = 'string_' + cfg.get('StringDb', 'version')
        self.fasta_version = cfg.get('StringDb', 'fasta_version')

    def _parse_config(self, properties):
        if isinstance(properties, str):
            cfg = self._parse_config_from_file(properties)
        else:
            cfg = self._parse_config_from_buffer(properties)

        if not _is_superset(cfg.sections(), self.SECTIONS):
            raise ValueError('some sections missing, expecting: {0}, got {1}'
                             .format(str(cfg.sections()), str(self.SECTIONS)))

        if PAXDB_STRINGDB_MAPPING[PAXDB_VERSION] != cfg.get('StringDb', 'version'):
            raise ValueError(
                'paxdb <-> stringdb version mismatch {0} <-> {1}'.format(PAXDB_VERSION, cfg.get('StringDb', 'version')))

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
