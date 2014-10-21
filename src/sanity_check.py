#!/usr/bin/python
# TODO check if input data is valid

import os
import glob
import subprocess
import logging
import logger
import stringdb


def check_for_duplicate_entries():
    pass


def compile_java_if_necessary():
    for java in glob.glob('*.java'):
        if not os.path.exists(java.replace('.java', '.class')):
            try:
                cmd_out = subprocess.check_output(['javac', java])
            except:
                logging.error('failed to compile %s: %s', java, cmd_out)


def export_from_postgresql():
    stringdb.export_from_postgresql()


if __name__ == '__main__':
    logger.configure_logging()
    export_from_postgresql()
    check_for_duplicate_entries()
    compile_java_if_necessary()
