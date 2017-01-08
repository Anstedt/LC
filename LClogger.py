#!/usr/bin/python

# LClogger.py
# One generic logger

import logging
from logging import handlers

logging.basicConfig(filename = '/var/log/LapCounter.log',
                    format   = '%(levelname)s %(asctime)s %(message)s',
                    level    = logging.INFO)

# Everyone can now use this to log
log = logging.getLogger("LapCounter")

# Create a handler to rotate logs
rotate_handler = handlers.RotatingFileHandler('/var/log/LapCounter.log', mode='a', maxBytes=10000, backupCount=1)

# Now add the handler
log.addHandler(rotate_handler)
