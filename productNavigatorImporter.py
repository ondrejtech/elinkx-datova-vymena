import csv
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

def proces_product_navigator_data(xml_files, connection, root_category, super_category):
    missing_attrs_path = "logs/missing_attribute.csv"
    # Otevřeme CSV v režimu přidání (a), aby se nevypisovalo znovu při každém spuštění
    with open(missing_attrs_path, mode='a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        # Můžeš odkomentovat řádek níže pro záhlaví jen při prvním spuštění
        # csv_writer.writerow(["ProId", "AttributeCode"])

        for xml_file in xml_files:
            xml_path = os.path.join('xml', root_category, super_category, xml_file)
            log(f"Zpracovávám soubor: {xml_file}")

            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()

                cursor = connection.cursor()

                for product in root.findall('.//ProductComplete'):
                    try:
                        data = {
                            'ProId': int(product.find('ProId').text),
                        }

                    except Exception as e:
                        log(f"Chyba při zpracování produktu ProId={data.get('ProId', 'NEZNÁMÝ')}: {e}")
                        continue

                    for logistic_data in product.findall('.//ProductNavigatorData'):
                        try:
                            attribute_code = logistic_data.find('AttributeCode')
                            value_code = logistic_data.find('ValueCode')

                            if attribute_code is None or value_code is None:
                                log(f"⚠️ Chybí AttributeCode nebo ValueCode pro ProId={data['ProId']}")
                                continue

                            data['attribute_code'] = int(attribute_code.text)
                            data['value_code'] = int(value_code.text)

                        except Exception as e:
                            log(f"Chyba při zpracování ProductNavigatorData pro ProId={data['ProId']}: {e}")
                            continue

                        # 💡 Ověření existence attribute_code
                        cursor.execute("SELECT 1 FROM category_attributes WHERE AttributeCode = %s", (data['attribute_code'],))
                        if cursor.fetchone() is None:
                            log(f"⚠️ AttributeCode {data['attribute_code']} neexistuje k productu {data['ProId']} – loguji.")
                            csv_writer.writerow([data['ProId'], data['attribute_code']])
                            continue

                        insert_query = """
                            INSERT INTO product_navigator_data (`ProId`, `AttributeCode`, `ValueCode`)
                            VALUES (%(ProId)s, %(attribute_code)s, %(value_code)s)
                            ON DUPLICATE KEY UPDATE
                                `AttributeCode` = VALUES(`AttributeCode`),
                                `ValueCode` = VALUES(`ValueCode`);
                        """

                        try:
                            cursor.execute(insert_query, data)
                        except Exception as e:
                            log(f"Chyba při SQL pro ProId={data['ProId']} AttributeCode={data['attribute_code']} ValueCode={data['value_code']}: {e}")

                connection.commit()

            except Exception as e:
                log(f"Chyba při zpracování souboru {xml_file}: {e}")

def main():
    log("🚀 Spouštím import navigacnich  dat...")
    connection = connect_db()

    for root_category in list_categories(xml_base_dir):
        root_path = os.path.join(xml_base_dir, root_category)

        for super_category in list_categories(root_path):
            super_path = os.path.join(root_path, super_category)
            xml_files = [f for f in os.listdir(super_path) if f.endswith('.xml')]

            log(f"📂 {root_category}/{super_category} - nalezeno {len(xml_files)} XML souborů.")

            proces_product_navigator_data(xml_files, connection, root_category, super_category)

    prague_time = datetime.now(pytz.timezone('Europe/Prague')).strftime('%Y-%m-%d %H:%M:%S')
    log(f"✅ Import dokončen v {prague_time}.")

if __name__ == "__main__":
    main()
