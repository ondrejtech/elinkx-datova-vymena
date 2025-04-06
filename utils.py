import os
import logging
import json
from config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "elinkx_import.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def log(msg):
    print(msg)
    logging.info(msg)

def log_soap_response(response, filename):
    with open(os.path.join(LOG_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(str(response))

def preview_data(data):
    log("🔪 Nahled dat:")
    log(json.dumps(data, indent=2)[:2000])


