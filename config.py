from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
}

SOAP_LOGIN = os.getenv('SOAP_LOGIN')
SOAP_PASSWORD = os.getenv('SOAP_PASSWORD')
WSDL_URL = os.getenv('WSDL_URL', 'https://private-ws-cz.elinkx.biz/service.asmx?wsdl')

# testovaci rezim (True/False)
TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'

LOG_DIR = os.getenv("LOG_DIR", "logs")


