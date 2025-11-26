
import logging
from io import StringIO as StringBuffer
import sys

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

### Setup the console handler with a StringIO object
### One for all the modules to use
log_capture_string = StringBuffer()
# log_capture_string.encoding = 'cp1251'
variableHandler = logging.StreamHandler(log_capture_string)
variableHandler.setLevel(logging.WARNING)
variableHandler.setFormatter(formatter)

consoleFormatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(consoleFormatter)

fileHandler = logging.FileHandler("execution.log", 'w+')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)

logger = logging.getLogger()   
logger.setLevel(logging.INFO) 
logger.addHandler(variableHandler)
logger.addHandler(consoleHandler)

LOCAL_DEBUG = False
if LOCAL_DEBUG:
    consoleHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

def getLogger(clazz):    
    logger = logging.getLogger(clazz)        
    return logger

def getLogMessages():
    ### Pull the contents back into a string and close the stream
    log_contents = log_capture_string.getvalue()
    log_capture_string.close()
    return log_contents