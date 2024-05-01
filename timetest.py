import logging
from datetime import datetime

# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
logging.basicConfig(
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S%Tz"
)
# formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%Y-%m-%d %H:%M:%S")

# Log a message with the current time in ISO-8601 format
# now = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

# Create a logger and set the custom formatter
# logger = logging.getLogger('custom_logger')
# handler = logging.StreamHandler()
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
# logger.setLevel(logging.INFO)

# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s : %(message)s')
# logging.basicConfig(filename='record.log',
#                 level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Secure this or something if actually deployed

# app.logger.setLevel(logging.INFO)  # Set log level to INFO
# handler = logging.FileHandler('app.log')  # Log to a file
# app.logger.addHandler(handler)
# formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%Y-%m-%d %H:%M:%ST%z")

# def utcformat(dt, timespecification='seconds'):
#     """convert datetime to string in UTC format (YYYY-mm-ddTHH:MM:SSZ)"""
#     iso_str = dt.astimezone(timezone.utc).isoformat(' ', timespecification)
#     return iso_str.replace('+00:00', 'TZ')

# def fromutcformat(utc_str, tz=None):
#     iso_str = utc_str.replace('Z', '+00:00')
#     return datetime.fromisoformat(iso_str).astimezone(tz)

# now = datetime.now(tz=timezone.utc)
# print(fromutcformat(utcformat(now)))