import os
import xml.etree.ElementTree as ET
import mysql.connector
from dotenv import load_dotenv
from utils import log
from datetime import datetime
import pytz

# Načti proměnné z .env
load_dotenv()

# Cesty a databáze
xml_base_dir = 'xml/'
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


def connect_db():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        log(f"✅ Připojeno k databázi {DB_NAME} na {DB_HOST} jako {DB_USER}.")
        return connection
    except Exception as e:
        log(f"❌ Nepodařilo se připojit k databázi: {e}")
        raise


def list_categories(base_dir):
    return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]


def proces_product_logistic_data(xml_files, connection, root_category, super_category):
    cursor = connection.cursor()
    total_files = len(xml_files)
    total_products = 0
    failed_products = 0

    for xml_file in xml_files:
        xml_path = os.path.join('xml', root_category, super_category, xml_file)

        prague_time = datetime.now(pytz.timezone('Europe/Prague')).strftime('%Y-%m-%d %H:%M:%S')
        log(f"📄 [{prague_time}] Zpracovávám soubor: {root_category}/{super_category}/{xml_file}")

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for product in root.findall('.//ProductComplete'):
                try:
                    pro_id = int(product.find('ProId').text)

                    # Import image URLs
                    for image in product.findall('.//ProductImage'):
                        image_url = image.find('URL')
                        if image_url is not None and image_url.text:
                            try:
                                cursor.execute(
                                    "INSERT INTO product_images (ProId, URL) VALUES (%s, %s)",
                                    (pro_id, image_url.text)
                                )
                            except Exception as e:
                                log(f"❌ Chyba při vkládání obrázku pro ProId={pro_id}: {e}")

                    connection.commit()
                    total_products += 1


                except Exception as e:
                    failed_products += 1
                    log(f"⚠️ Chyba při zpracování produktu ProId={product.find('ProId').text if product.find('ProId') is not None else '?'}: {e}")

        except Exception as e:
            log(f"❌ Chyba při načítání/parsing XML souboru {xml_file}: {e}")

    log(f"🔄 Souhrn pro {super_category}: Zpracováno {total_products} produktů, chyb {failed_products}.")


def main():
    log("🚀 Spouštím import logistických dat...")
    connection = connect_db()

    for root_category in list_categories(xml_base_dir):
        root_path = os.path.join(xml_base_dir, root_category)

        for super_category in list_categories(root_path):
            super_path = os.path.join(root_path, super_category)
            xml_files = [f for f in os.listdir(super_path) if f.endswith('.xml')]

            log(f"📂 {root_category}/{super_category} - nalezeno {len(xml_files)} XML souborů.")

            proces_product_logistic_data(xml_files, connection, root_category, super_category)

    prague_time = datetime.now(pytz.timezone('Europe/Prague')).strftime('%Y-%m-%d %H:%M:%S')
    log(f"✅ Import dokončen v {prague_time}.")


if __name__ == "__main__":
    main()
