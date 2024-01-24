#!/usr/bin/python

# this is for the spectral counting calculating protein abundance
# and raw spectral count and mapped peptide
#

import shlex
import subprocess
import logging
from pathlib import Path

from paxdb.config import PaxDbConfig

cfg = PaxDbConfig()


# def calculate_abundance_and_raw_spectral_counts(pepfile, scfile, speid, fasta_dir, fasta_ver='11.5'):
#     """
#     takes peptide counts and fasta file and produces protein abundance + counts
#     """

#     cmd = "java -Xms512m ComputeAbundanceswithSC  '{1}' '{2}/fasta.v{3}.{0}.fa'"
#     cmd = cmd.format(speid, pepfile, fasta_dir, fasta_ver)
#     try:
#         cmd_out = subprocess.check_output(shlex.split(cmd))
#         with open(scfile, "wb") as ofile:
#             ofile.write(cmd_out)
#         return scfile
#     except:
#         logging.exception('failed to run %s: %s', cmd)
#     return None

def calculate_abundance_and_raw_spectral_counts(pepfile, scfile, speid, fasta_dir, fasta_ver='11.5'):
    cmd = 'python3 ' + str(Path(__file__).parent.parent / 'ComputeAbundanceswithSC.py') + " -s '{1}' -f '{2}/fasta.v{3}.{0}.fa'"
    cmd = cmd.format(speid, pepfile, fasta_dir, fasta_ver)
    try:
        cmd_out = subprocess.check_output(shlex.split(cmd))
        with open(scfile, "wb") as ofile:
            ofile.write(cmd_out)
        return scfile
    except:
        logging.exception('failed to run %s: %s', cmd)
    return None
    
def map_peptide(pepfile, out, speid, fasta_dir, fasta_ver='11.5'):
    """
    maps peptides to proteins: takes peptide counts and fasta file 
    and produces protein/peptide/counts.

    This is currently used for the download page ("Accessory files"
    catalog as "Mapped peptides"). The original idea was to show
    user our way of mapping peptides.

    """
    # out = get_output_dir(speid) + get_filename_no_extension(pepfile) + "_peptide.txt"
    cmd = "python3 ComputeAbundanceswithSC.py -s '{1}' -f '{2}/fasta.v{3}.{0}.fa' -p"
    cmd = cmd.format(speid, pepfile, fasta_dir, fasta_ver)

    with open(out, "w") as ofile:
        if out.endswith('int'):
            ofile.write("#string_external_id	peptide_sequence	peak_intensity\n")
        else:
            ofile.write("#string_external_id	peptide_sequence	spectral_count\n")
            
        ofile.flush()
        subprocess.Popen(shlex.split(cmd), stdout=ofile).wait()

