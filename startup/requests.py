

# Increase the number of connections available
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


r_session = requests.Session()
r_session.mount('http://', HTTPAdapter(pool_connections=30, pool_maxsize=100, max_retries=Retry(5, status_forcelist=[503], method_whitelist=None, backoff_factor=0.2), pool_block=True))
r_session.mount('https://', HTTPAdapter(pool_connections=30, pool_maxsize=100, max_retries=Retry(5, status_forcelist=[503], method_whitelist=None, backoff_factor=0.2), pool_block=True))

