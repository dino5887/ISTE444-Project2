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
print(logging.info(f'My log message at hello'))