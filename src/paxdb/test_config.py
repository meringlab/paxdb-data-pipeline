import unittest

from paxdb.config import PaxDbConfig

try:
    # python2
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

VALID_CONFIG = """
[StringDb]
version: 10_0
fasta_version: 10.0
[postgresql]
url:  www.uzh.ch
user: imls_user
pass: imls_pass
port: 5432
[Google_account]
user: paxdb@gmail.com
pass: hash_s3cr3t
spreadsheet_key: aaBB
"""


class TestPaxDbConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.CONFIG = StringIO(VALID_CONFIG)

    def test_valid_config(self):
        c = PaxDbConfig(self.CONFIG)
        self.assertEquals('string_10_0', c.string_db)
        self.assertEquals('host=www.uzh.ch port=5432 '
                          'user=imls_user dbname=string_10_0',
                          c.pg_url)
        self.assertEquals('paxdb@gmail.com', c.google_user)

    def test_if_versions_match(self):
        '''paxdb v3.0 is based on stringdb v9.0, v4.0 on stringdb v10, etc'''
        with self.assertRaises(ValueError):
            c = PaxDbConfig(StringIO(VALID_CONFIG.replace('10_0', '9_1')))

    def test_fail_if_section_missing(self):
        props = StringIO("[StringDb]\nversion: 10\n"
                         "[postgresql]\nurl: url")
        with self.assertRaises(ValueError):
            c = PaxDbConfig(props)

    def test_fail_if_option_missing(self):
        props = StringIO("[StringDb]\nversion: 10\n"
                         "[postgresql]\nurl: url\n"
                         "[Google_account]\nuser: user")
        try:
            c = PaxDbConfig(props)
            self.fail("should fail, missing options")
        except:
            pass


if __name__ == '__main__':
    unittest.main()

