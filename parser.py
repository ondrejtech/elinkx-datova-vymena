from zeep import Client
from zeep.transports import Transport
from requests import Session
from dotenv import load_dotenv
import os
import requests
import mysql.connector
import sys
from datetime import datetime
import pytz
from utils import log


load_dotenv()

# Globální konfigurace
WSDL_URL = os.getenv("WSDL_URL")
SOAP_LOGIN = os.getenv("SOAP_LOGIN")
SOAP_PASSWORD = os.getenv("SOAP_PASSWORD")
DB_CONFIG = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_NAME")
}

ICON_MAP = {
    "IT": "💻", "Elektronika": "📱", "Domácnost": "🏠",
    "Velké spotřebiče": "🩺", "Sport a volný čas": "⚽",
    "Hobby a zahrada": "🌿", "Péče o tělo": "🧴"
}


def get_icon(name):
    return ICON_MAP.get(name, "🔹")


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def fetch_categories(cursor, query, params=()):
    cursor.execute(query, params)
    return cursor.fetchall()


def clean_name(name):
    return ''.join(c for c in ''.join(word.upper() if len(word) == 2 else word.capitalize()
                                      for word in name.split() if word.lower() != 'a') if c.isalnum())


def soap_request(root_name, super_name, cat_name, cat_code, super_code, root_code):
    try:
        session = Session()
        transport = Transport(session=session)
        client = Client(wsdl=WSDL_URL, transport=transport)

        response = client.service.getProductCatalogueFullNavFilterSOAPDownloadXML(
            login=SOAP_LOGIN,
            password=SOAP_PASSWORD,
            onStock=True,
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


def download_xml(url, root_name, super_name, cat_name):
    safe_name = clean_name(cat_name)
    filename = f"{safe_name}.xml"

    directory = os.path.join(
        "xml",
        clean_name(root_name),
        clean_name(super_name)
    )
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, filename)

    try:
        res = requests.get(url)
        with open(file_path, 'wb') as f:
            f.write(res.content)
        log(f"✅ XML downloaded: {file_path} [timestamp: {datetime.now(pytz.timezone('Europe/Prague')).isoformat()}]")
    except Exception as e:
        log(f"❌ Download failed: {e}")


def process_category(cursor, root, super_cat, cat):
    log(f"🔄 Processing: {cat['CategoryName']}")
    response = soap_request(
        root['SuperCategoryName'], super_cat['SuperCategoryName'],
        cat['CategoryName'], cat['CategoryCode'],
        super_cat['SuperCategoryCode'], root['SuperCategoryCode']
    )
    if response and getattr(response, 'isReady', False) and getattr(response, 'url', None):
        download_xml(response.url, root['SuperCategoryName'], super_cat['SuperCategoryName'], cat['CategoryName'])
    else:
        log("⚠️ Response not ready or missing URL.")


def process_all(cursor):
    roots = fetch_categories(cursor, "SELECT * FROM super_categories WHERE ParentSuperCategoryCode = 0")
    for root in roots:
        supers = fetch_categories(cursor, "SELECT * FROM super_categories WHERE ParentSuperCategoryCode = %s", (root['SuperCategoryCode'],))
        for super_cat in supers:
            cats = fetch_categories(cursor, "SELECT * FROM categories WHERE SuperCategoryCode = %s", (super_cat['SuperCategoryCode'],))
            for cat in cats:
                process_category(cursor, root, super_cat, cat)


def process_selection(cursor, root_code):
    root = fetch_categories(cursor, "SELECT * FROM super_categories WHERE SuperCategoryCode = %s", (root_code,))
    if not root:
        log("❌ Invalid root category.")
        return
    root = root[0]

    supers = fetch_categories(cursor, "SELECT * FROM super_categories WHERE ParentSuperCategoryCode = %s", (root_code,))
    print("\n--- Super Categories ---")
    print("0. 📂 All")
    for s in supers:
        print(f"{get_icon(s['SuperCategoryName'])} {s['SuperCategoryCode']}. {s['SuperCategoryName']}")

    inp = input("Select super category: ")
    if inp == "01":
        sys.exit()
    selected = int(inp)

    if selected == 0:
        for super_cat in supers:
            cats = fetch_categories(cursor, "SELECT * FROM categories WHERE SuperCategoryCode = %s", (super_cat['SuperCategoryCode'],))
            for cat in cats:
                process_category(cursor, root, super_cat, cat)
    else:
        super_cat = fetch_categories(cursor, "SELECT * FROM super_categories WHERE SuperCategoryCode = %s", (selected,))
        if not super_cat:
            log("❌ Invalid super category.")
            return
        super_cat = super_cat[0]

        cats = fetch_categories(cursor, "SELECT * FROM categories WHERE SuperCategoryCode = %s", (selected,))
        print("\n--- Categories ---")
        print("0. 📂 All")
        for c in cats:
            print(f"{get_icon(c['CategoryName'])} {c['CategoryCode']}. {c['CategoryName']}")

        inp = input("Select category: ")
        if inp == "01":
            sys.exit()
        selected_cat = int(inp)

        if selected_cat == 0:
            for cat in cats:
                process_category(cursor, root, super_cat, cat)
        else:
            cat = fetch_categories(cursor, "SELECT * FROM categories WHERE CategoryCode = %s", (selected_cat,))
            if not cat:
                log("❌ Invalid category.")
                return
            process_category(cursor, root, super_cat, cat[0])


def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        roots = fetch_categories(cursor, "SELECT * FROM super_categories WHERE ParentSuperCategoryCode = 0")
        print("\n--- Root Categories ---")
        print("0. 📂 All")
        for root in roots:
            print(f"{get_icon(root['SuperCategoryName'])} {root['SuperCategoryCode']}. {root['SuperCategoryName']}")

        selected = input("Select root category (0 for all, 01 to exit): ")
        if selected == "01":
            log("⛔ Terminated by user.")
            return

        selected_code = int(selected)
        if selected_code == 0:
            process_all(cursor)
        else:
            process_selection(cursor, selected_code)

    except Exception as e:
        log(f"❌ Unexpected error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    main()
