import os
from Constants import LOG_FILE_PATH

def clearLog():
    try:
        os.remove(LOG_FILE_PATH) 
    except FileNotFoundError:
        pass

def log(message):
    log_file = open(LOG_FILE_PATH,"a+")
    log_file.write(str(message) + "\n")
    log_file.close()