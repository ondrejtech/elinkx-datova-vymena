from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session
from dotenv import load_dotenv
import os
import requests
import mysql.connector
import sys

def getProductCatalogueFullNavFilterDownloadXML():
    load_dotenv()

    # SOAP credentials
    WSDL_URL = os.getenv("WSDL_URL")
    SOAP_LOGIN = os.getenv("SOAP_LOGIN")
    SOAP_PASSWORD = os.getenv("SOAP_PASSWORD")

    # DB credentials
    DB_CONFIG = {
        'host': os.getenv("DB_HOST"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'database': os.getenv("DB_NAME")
    }

    # Connect to DB and fetch root super categories
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT SuperCategoryCode, SuperCategoryName, ParentSuperCategoryCode FROM super_categories WHERE ParentSuperCategoryCode = 0")
    root_super_categories = cursor.fetchall()

    print("\n--- Root Category ---")
    print("0. Všechny root kategorie")
    for idx, super_cat in enumerate(root_super_categories, start=1):
        print(f"{idx}. {super_cat['SuperCategoryName']} (Code: {super_cat['SuperCategoryCode']})")

    selected_input = input("Zadej čísla root kategorií oddělená čárkou (např. 1,3), 0 pro všechny nebo konec pro ukončení: ")
    if selected_input.strip().lower() == "konec":
        print("⛔ Skript ukončen uživatelem.")
        sys.exit()
    if selected_input.strip() == "0":
        selected_supers = root_super_categories
    else:
        selected_indexes = [int(i.strip()) - 1 for i in selected_input.split(',') if i.strip().isdigit()]
        selected_supers = [root_super_categories[i] for i in selected_indexes if 0 <= i < len(root_super_categories)]

    # Výpis kategorií kde SuperCategoryCode = CategoryCode
    print(selected_supers)
    cursor.execute("SELECT * FROM categories WHERE SuperCategoryCode = CategoryCode")
    all_supercategories = cursor.fetchall()
    print("\n--- SuperCategory z tabulky categories (kde SuperCategoryCode = CategoryCode) ---")
    for idx, sc in enumerate(all_supercategories, start=1):
        print(f"{idx}. {sc['SuperCategory']} (CategoryCode: {sc['CategoryCode']})")

    # Výběr super kategorií z tabulky categories dle názvu
    supercat_name_input = input("\nZadej název SuperCategory (nebo více oddělených čárkami) z tabulky categories nebo 'konec' pro ukončení: ")
    if supercat_name_input.strip().lower() == "konec":
        print("⛔ Skript ukončen uživatelem.")
        sys.exit()
    supercat_names = [s.strip() for s in supercat_name_input.split(',') if s.strip()]

    selected_super_categories_from_cat = []
    for name in supercat_names:
        cursor.execute("SELECT DISTINCT SuperCategory, CategoryCode, CategoryName FROM categories WHERE SuperCategory = %s", (name,))
        selected_super_categories_from_cat.extend(cursor.fetchall())

    cursor.close()
    conn.close()

    # SOAP client
    session = Session()
    transport = Transport(session=session)
    history = HistoryPlugin()
    client = Client(wsdl=WSDL_URL, transport=transport, plugins=[history])

    # Příprava vstupů
    combined_requests = []

    for super_cat in selected_supers:
        combined_requests.append({
            'super_code': super_cat['SuperCategoryCode'],
            'super_name': super_cat['SuperCategoryName'],
            'parent_super': super_cat['ParentSuperCategoryCode'],
            'cat_code': 0,
            'cat_name': ""
        })

    for cat in selected_super_categories_from_cat:
        combined_requests.append({
            'super_code': 0,
            'super_name': cat['SuperCategory'],
            'parent_super': 0,
            'cat_code': cat['CategoryCode'],
            'cat_name': cat['CategoryName']
        })

    # SOAP požadavky
    for req in combined_requests:
        params = {
            "login": SOAP_LOGIN,
            "password": SOAP_PASSWORD,
            "onStock": True,
            "filter": {
                "superCategory": {
                    "ProductCategoryList": {
                        "ProductCategory": [None, None]
                    },
                    "SuperCategoryCode": req['super_code'],
                    "SuperCategoryName": req['super_name'],
                    "ParentSuperCategoryCode": req['parent_super']
                },
                "category": {
                    "CategoryCode": req['cat_code'],
                    "CategoryName": req['cat_name'],
                    "ProductAttributeList": {
                        "ProductCategoryAttribute": [None, None]
                    },
                    "ImageList": {
                        "ProductCategoryImage": [None, None]
                    }
                },
                "productProducerList": {
                    "ProductProducer": []
                },
                "productNavigatorDataList": {
                    "ProductNavigatorData": []
                }
            }
        }

        print(f"\n➡️ Odesílám požadavek pro super kategorii '{req['super_name']}'...")
        response = client.service.getProductCatalogueFullNavFilterSOAPDownloadXML(**params)

        print("\n✅ Odpověď ze serveru:")
        status = response.ProductListStatus
        print(f"- isReady: {status.isReady}")
        print(f"- fileName: {status.fileName}")
        print(f"- url: {status.url}")

        if status.isReady:
            print("\n📥 Stahuji XML soubor...")
            try:
                res = requests.get(status.url)
                file_path = status.fileName or f"products_{req['super_name']}.xml"
                with open(file_path, "wb") as f:
                    f.write(res.content)
                print(f"✅ Soubor uložen jako: {file_path}")
            except Exception as e:
                print(f"❌ Chyba při stahování: {e}")
        else:
            print("⚠️ Soubor ještě není připraven. Zkuste to později.")

if __name__ == "__main__":
    getProductCatalogueFullNavFilterDownloadXML()
