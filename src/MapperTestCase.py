import Mapper 
import unittest

from StringIO import StringIO

class MapperTest(unittest.TestCase):

    def setUp(self):
        self.species = 42
        self.external_ids_map = {'42.p1': 1, '42.p2': 2, '42.p3' : 3}
        self.names = {'n11': 1,'n12': 1, 'n2': 2}
        self.m = Mapper.DatasetMapper(42, self.external_ids_map, self.names)

    def test_empty_mapping(self):
        e = self.m.map_to_external_ids({})
        self.assertEquals(0, len(e))

    def test_all_map_to_external(self):
        e = self.m.map_to_external_ids({'p1': '47.2'})
        self.assertEquals({'p1': '42.p1'},e)

    def test_mixed_external_names(self):
        e = self.m.map_to_external_ids({'p1': '-1', 'n2': '-1'})
        self.assertEquals({'p1': '42.p1', 'n2': '42.p2'},e)

    def test_names_only(self):
        e = self.m.map_to_external_ids({'n2': '-1'})
        self.assertEquals({'n2': '42.p2'},e)

    def test_conflict(self):
        e = self.m.map_to_external_ids({'p1': '-1', 'n1': '-1'})
        self.assertEquals({'p1': '42.p1'},e)

    def test_to_external_id(self):
        self.assertEquals('12.p1', Mapper.to_external_id(12,'p1'))
        self.assertEquals('12.p1', Mapper.to_external_id('12','p1'))

class EntriesReaderTest(unittest.TestCase):
    def test_single_entry(self):
        e = Mapper.read_entries(StringIO('p1\t12\n\n'))
        self.assertEquals(1, len(e))
        self.assertEquals('12',e['p1'])

    def test_multiple_entries(self):
        e = Mapper.read_entries(StringIO('p1\t12\np2\t99.1\t47'))
        self.assertEquals(2, len(e))
        self.assertEquals('12',e['p1'])
        self.assertEquals('99.1\t47',e['p2'])
    
    def test_skip_headers(self):
        e = Mapper.read_entries(StringIO(' # a 1\n#b 2 2\np1\t12\n'))
        self.assertEquals(1, len(e))
        self.assertEquals('12',e['p1'])


if __name__ == '__main__':
    unittest.main()
