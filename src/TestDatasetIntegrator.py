#!/usr/bin/python

from DatasetIntegrator import *

import unittest
from tempfile import mkdtemp
import shutil
import random
from os.path import join

class TestDatasetIntegrator(unittest.TestCase):
    class RRunnerMock():
        def __init__(self, tmpdir):
            self.tmpdir=tmpdir
        def run(self, args):
            score= '1.0' if args[2] == '1.0' and args[3] == '0.3' else str(random.random())
            integrated = 'integrated-'+str(args[2])+'_'+str(args[3])+'.txt'
            with open(join(self.tmpdir,integrated),'w'):
                pass #just to make integrate() work
            return join(self.tmpdir,integrated)+'\n'+score

    def setUp(self):
        self.mrna_species = ['4896', '4932', '511145', '6239', '7227']
        self.tmpdir=mkdtemp()

    def test_integrate_two_datasets(self):
        integrator = DatasetIntegrator(self.tmpdir+'4896-integrated.txt',['d1.txt','d2.txt'],self.RRunnerMock(self.tmpdir))
        weights = integrator.integrate()
        self.assertEqual([1.0, 0.3], weights)

    def test_integrate_more_than_two_datasets(self):
        multi_integrator = DatasetIntegrator(self.tmpdir+'4932-integrated.txt',['d1.txt','d2.txt','d3.txt'],self.RRunnerMock(self.tmpdir))
        weights = multi_integrator.integrate()
        self.assertEqual([1.0, 0.3, 0.3], weights)

    def test_species_with_mrna_data(self):
        species = species_mrna()
        self.assertEqual(set(self.mrna_species), set(species))

    def tearDown(self):
            shutil.rmtree(self.tmpdir)

if __name__ == '__main__':
    unittest.main()
