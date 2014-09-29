#!/usr/bin/python

from DatasetIntegrator import *

import unittest
from tempfile import mkdtemp
import shutil
import random


class TestDatasetIntegrator(unittest.TestCase):
    class RRunnerMock():
        def __init__(self):
            pass
        def run(self, args):
            if args[2] == 0.7 and args[3] == 0.3:
                return '100'
            return str(random.random())

    def setUp(self):
        self.mrna_species = ['4896', '4932', '511145', '6239', '7227']
        self.tmpdir=mkdtemp()
        self.integrator = DatasetIntegrator('4896',['d1.txt','d2.txt'],'WHOLE',self.tmpdir,'/tmp/input_datasets/',self.RRunnerMock())

    def test_integrate(self):
        weights = self.integrator.integrate()
        self.assertEqual([0.7, 0.3], weights)

    def test_species_with_mrna_data(self):
        species = enumerate_species_with_mrna()
        self.assertEqual(set(self.mrna_species), set(species))

    def test_species_without_mrna_data(self):
        species = enumerate_species_without_mrna()
        self.assertTrue(set(self.mrna_species).isdisjoint(set(species)))


    def tearDown(self):
            shutil.rmtree(self.tmpdir)


if __name__ == '__main__':
    unittest.main()
