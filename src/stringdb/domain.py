"""
Created on Oct 16, 2014

@author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
"""

import re

# requires pip: sudo apt-get install python3-setuptools && sudo easy_install3 pip
from pip._vendor.distlib.util import cached_property


class Protein(object):
    """
    Represents a StringDb protein 
    """

    _externalIdPattern = re.compile(r'(\d+)\.\w+')

    def __init__(self, internal_id, external_id, preferred_name):
        if type(internal_id) != int or internal_id < 1:
            raise ValueError("internal id must be int > 1")
        if type(external_id) != str or not Protein._externalIdPattern.match(external_id):
            raise ValueError("invalid external id: " + external_id)
        self.id = internal_id
        self.externalId = external_id
        self.name = preferred_name

    @cached_property
    def speciesId(self):
        return int(Protein._externalIdPattern.match(self.externalId).group(1))

    # @cached_property
    def __repr__(self):
        return "Protein(id: {0.id}, externalId: {0.externalId}, name: {0.name})".format(self)

    def __str__(self):
        return "id: {0.id}, externalId: {0.externalId}, name: {0.name}".format(self)


class Species(object):
    def __init__(self, id, name, proteins_list):
        self.id = id
        self.name = name
        self.proteins = proteins_list
        # TODO init mappings (internal-external...)
