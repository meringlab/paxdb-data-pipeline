#!/usr/bin/python

# this is for the spectral counting calculating protein abundance
# and raw spectral count and mapped peptide
#

import os
import shlex
import subprocess
import logging

from config import PaxDbConfig


cfg = PaxDbConfig()


def calculate_abundance_and_raw_spectral_counts(pepfile, scfile, speid, fasta_dir, fasta_ver='10.0'):
    """
    takes peptide counts and fasta file and produces protein abundance + counts
    """

    cmd = "java -Xms512m ComputeAbundanceswithSC -s {0} '{1}' '{2}/fasta.v{3}.{0}.fa'"
    cmd = cmd.format(speid, pepfile, fasta_dir, fasta_ver)
    try:
        cmd_out = subprocess.check_output(shlex.split(cmd))
        with open(scfile, "wb") as ofile:
            ofile.write(cmd_out)
        return scfile
    except:
        logging.exception('failed to run %s: %s', cmd)
    return None


def map_peptide(pepfile, out, speid, fasta_dir, fasta_ver='10.0'):
    """
    maps peptides to proteins: takes peptide counts and fasta file 
    and produces protein/peptide/counts.

    This is currently used for the download page ("Accessory files"
    catalog as "Mapped peptides"). The original idea was to show
    user our way of mapping peptides.

    """
    # out = get_output_dir(speid) + get_filename_no_extension(pepfile) + "_peptide.txt"
    cmd = "java -Xms512m ComputeAbundancesMappep -p 4 -s {0} '{1}' '{2}/fasta.v{3}.{0}.fa' | tee > {4} "
    cmd = cmd.format(speid, pepfile, fasta_dir, fasta_ver, out)
    if os.path.isfile(out):
        return
    with open(out, "a") as ofile:
        ofile.write("#string_external_id	peptide_sequence	spectral_count\n")
        ofile.flush()
        subprocess.Popen(shlex.split(cmd), stdout=ofile).wait()
