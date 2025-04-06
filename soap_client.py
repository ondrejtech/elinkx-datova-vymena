from zeep import Client
from zeep.helpers import serialize_object
from config import SOAP_LOGIN, SOAP_PASSWORD, WSDL_URL
from utils import log_soap_response

def get_navigator_data():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getNavigator(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "navigator_response.xml")
    return serialize_object(response)

def get_product_producers():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getProductProducerList(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "producers_response.xml")
    return serialize_object(response)

def get_commodities():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getProductCommodityList(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "commodities_response.xml")
    return serialize_object(response)

def get_product_index():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getProductIndexTree1(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "product_index_response.xml")
    return serialize_object(response)

def get_transportation():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getTransportationList(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "transportation_list.xml")
    return serialize_object(response)
