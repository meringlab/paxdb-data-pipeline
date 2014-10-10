#!/usr/bin/python
#
# util module to configure logging
# @author: Milan Simonovic <milan.simonovic@imls.uzh.ch>
#

import sys
import logging
import optparse

def configure_logging(defaultLogFile=None):
    logfile=defaultLogFile
    loglevel='INFO'

    if len(sys.argv) > 0:
        parser = optparse.OptionParser()
        parser.add_option( "-l", "--logfile",
                       help = "use FILE as log file (default: paxdb.log)",
                       action = "store", dest = "logfile" )
        parser.add_option( "-v", "--loglevel",
                       help = "set loglevel (default: DEBUG)",
                       action = "store", dest = "loglevel",
                       default = 'DEBUG' )
        (cmd_options, args) = parser.parse_args(sys.argv)
        if hasattr(cmd_options, 'logfile'):
            logfile = cmd_options.logfile
        if hasattr(cmd_options, 'loglevel'):
            loglevel = cmd_options.loglevel

    # Convert to upper case to allow the user to specify --log=DEBUG or --log=debug
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(filename=logfile, level=numeric_level, 
                        format='%(asctime)s %(funcName)s %(levelname)s %(message)s')

if __name__ == "__main__":
    configure_logging()
    logging.error('hello world')
    logging.warn('hello world')
    logging.info('hello world')
    logging.debug('hello world')

