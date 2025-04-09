from requests import Session
from zeep import Client
from zeep.helpers import serialize_object
from zeep.transports import Transport
from config import SOAP_LOGIN, SOAP_PASSWORD, WSDL_URL
from utils import log, log_soap_response

def get_navigator_data():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getNavigator(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "navigator_response.xml")
    return serialize_object(response)

def get_product_categories_image():
    client = Client(wsdl=WSDL_URL)
    response = client.service.getProductCategoryList(SOAP_LOGIN, SOAP_PASSWORD)
    log_soap_response(response, "product_category_list.xml")
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

def getProductCatalogueFullNavFilterSOAPDownloadXML(root_name, super_name, cat_name, cat_code, super_code, root_code):
    try:
        session = Session()
        transport = Transport(session=session)
        client = Client(wsdl=WSDL_URL, transport=transport)

        response = client.service.getProductCatalogueFullNavFilterSOAPDownloadXML(
            login=SOAP_LOGIN,
            password=SOAP_PASSWORD,
            onStock='true',
            filter={
                "superCategory": {
                    "ProductCategoryList": {"ProductCategory": [None, None]},
                    "SuperCategoryCode": super_code,
                    "SuperCategoryName": super_name,
                    "ParentSuperCategoryCode": root_code
                },
                "category": {
                    "CategoryCode": cat_code,
                    "CategoryName": cat_name,
                    "ProductAttributeList": {"ProductCategoryAttribute": [None, None]},
                    "ImageList": {"ProductCategoryImage": [None, None]}
                },
                "productProducerList": {"ProductProducer": []},
                "productNavigatorDataList": {"ProductNavigatorData": []}
            }
        )

        return response.ProductListStatus

    except Exception as e:
        log(f"❌ SOAP request failed: {e}")
        return None