
import logging
from io import StringIO as StringBuffer
import sys

# Force UTF-8 encoding for stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

outputHandler = logging.StreamHandler(sys.stdout)
outputHandler.setLevel(logging.WARNING)
outputHandler.setFormatter(formatter)

consoleFormatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stderr)
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(consoleFormatter)

fileHandler = logging.FileHandler("execution.log", 'w+')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)

logger = logging.getLogger()   
logger.setLevel(logging.INFO) 
logger.addHandler(outputHandler)
logger.addHandler(consoleHandler)

LOCAL_DEBUG = False
if LOCAL_DEBUG:
    consoleHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

def getLogger(clazz):    
    logger = logging.getLogger(clazz)        
    return logger
