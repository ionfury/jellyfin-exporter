import os
import logging
import requests
import threading
import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from collectors import JellyfinSessions, JellyfinUsers, JellyfinItems
from datetime import datetime

JELLYFIN_EXPORTER_PORT = int(os.getenv("JELLYFIN_EXPORTER_PORT", 8080))
JELLYFIN_EXPORTER_URL = os.getenv("JELLYFIN_EXPORTER_URL", "localhost:9090")
JELLYFIN_EXPORTER_API_KEY = os.getenv("JELLYFIN_EXPORTER_API_KEY", "")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Starting jellyfin_exporter for '%s' on port: %d", str(JELLYFIN_EXPORTER_URL), JELLYFIN_EXPORTER_PORT)
logging.debug("Starting with api key '%s'", JELLYFIN_EXPORTER_API_KEY)


def request_api(action):
    url = "{}{}?api_key={}".format(JELLYFIN_EXPORTER_URL, action, JELLYFIN_EXPORTER_API_KEY)
    start = time.time()
    data = requests.get(url).json()
    elapsed = time.time() - start
    logging.info("Request to %s returned in %s", url, elapsed)
    return data


def get_timestamp(date):
    return int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp())


REGISTRY.register(JellyfinSessions(request_api, logging.critical))
REGISTRY.register(JellyfinUsers(request_api, get_timestamp, logging.critical))
REGISTRY.register(JellyfinItems(request_api, logging.critical))
start_http_server(JELLYFIN_EXPORTER_PORT)

e = threading.Event()
e.wait()
