import logging
import logging.config
import os

TEMP_BASE_DIR: str = os.path.dirname(os.path.abspath(__file__)) 
TEMP_LOGS_DIR = os.path.join(os.path.abspath(os.path.join(TEMP_BASE_DIR, "../")), 'config.ini')
logging.config.fileConfig(fname=TEMP_LOGS_DIR, disable_existing_loggers=False)

def logger_config(module):
    '''
    loggers:
    
    @parameter debug
    @parameter info
    @parameter warning
    @parameter error
    @parameter critical
    @parameter exception
    @returns logger
    '''
    logger = logging.getLogger(module)
    return logger