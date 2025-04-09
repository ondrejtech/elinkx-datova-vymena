import os
import xml.etree.ElementTree as ET
import mysql.connector
from dotenv import load_dotenv
from utils import log

# Načti proměnné z .env
load_dotenv()

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

def process_xml_and_save_to_db(xml_files, connection, root_category, super_category):
    for xml_file in xml_files:
        xml_path = os.path.join('xml', root_category, super_category, xml_file)
        log(f"📄 Zpracovávám soubor: Root: {root_category}/{super_category}/{xml_file}")

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            cursor = connection.cursor()
            for product in root.findall('.//ProductComplete'):
                try:
                    data = {
                        'ProId': int(product.find('ProId').text),
                        'Code': product.find("Code").text.strip(),
                        'Name': product.find('Name').text,
                        'YourPrice': float(product.find('YourPrice').text),
                        'YourPriceWithFees': float(product.find('YourPriceWithFees').text),
                        'CommodityCode': product.find('CommodityCode').text,
                        'GarbageFee': float(product.find('GarbageFee').text),
                        'AuthorFee': float(product.find('AuthorFee').text),
                        'ValuePack': float(product.find('ValuePack').text),
                        'ValuePackQty': float(product.find('ValuePackQty').text),
                        'Warranty': product.find('Warranty').text,
                        'CommodityName': product.find('CommodityName').text,
                        'DealerPrice': float(product.find('DealerPrice').text),
                        'EndUserPrice': float(product.find('EndUserPrice').text),
                        'Vat': float(product.find('Vat').text),
                        'PartNumber': product.find('PartNumber').text,
                        'OnStock': product.find('OnStock').text == 'true',
                        'OnStockText': product.find('OnStockText').text,
                        'Status': product.find('Status').text,
                        'ProducerName': product.find('ProducerName').text,
                        'RateOfDutyCode': product.find('RateOfDutyCode').text,
                        'EANCode': product.find('EANCode').text,
                        'NameB2C': product.find('NameB2C').text,
                        'DescriptionShort': product.find('DescriptionShort').text,
                        'Description': product.find('Description').text,
                        'IsTop': product.find('IsTop').text == 'true',
                        'InfoCode': product.find('InfoCode').text,
                        'WarrantyTerm': product.find("WarrantyTerm").text.strip() or None,
                        'WarrantyUnit': product.find("WarrantyUnit").text.strip() or None,
                        'PartNumber2': product.find('PartNumber2').text,
                        'DateAvailible': product.find('DateAvailible').text,
                        'DealerPrice1': float(product.find('DealerPrice1').text),
                        'Unit': product.find('Unit').text,
                        'OnStockCount': float(product.find('OnStockCount').text),
                        'ImgCount': int(product.find('ImgCount').text),
                        'ImgLastChanged': product.find('ImgLastChanged').text,
                        'ProducerCode': product.find('ProducerCode').text,
                        'CategoryCode': int(product.find('CategoryCode').text),
                        'B2C': product.find('B2C').text == 'true',
                        'B2FPrice': float(product.find('B2FPrice').text),
                        'RCStatus': product.find('RCStatus').text,
                        'RCCode': product.find('RCCode').text,
                        'IsPremium': product.find('IsPremium').text == 'true',
                        'ExtInfoCodes': product.find('ExtInfoCodes').text
                    }

                    insert_query = """
                    INSERT INTO products (ProId, Code, Name, YourPrice, YourPriceWithFees, CommodityCode,
                        GarbageFee, AuthorFee, ValuePack, ValuePackQty, Warranty,
                        CommodityName, DealerPrice, EndUserPrice, Vat, PartNumber, OnStock,
                        OnStockText, Status, ProducerName, RateOfDutyCode, EANCode,
                        NameB2C, DescriptionShort, Description, IsTop, InfoCode, WarrantyTerm,
                        WarrantyUnit, PartNumber2, DateAvailible, DealerPrice1, Unit,
                        OnStockCount, ImgCount, ImgLastChanged, ProducerCode, CategoryCode,
                        B2C, B2FPrice, RCStatus, RCCode, IsPremium, ExtInfoCodes)
                    VALUES (%(ProId)s, %(Code)s, %(Name)s, %(YourPrice)s, %(YourPriceWithFees)s, %(CommodityCode)s,
                        %(GarbageFee)s, %(AuthorFee)s, %(ValuePack)s, %(ValuePackQty)s, %(Warranty)s,
                        %(CommodityName)s, %(DealerPrice)s, %(EndUserPrice)s, %(Vat)s, %(PartNumber)s, %(OnStock)s,
                        %(OnStockText)s, %(Status)s, %(ProducerName)s, %(RateOfDutyCode)s, %(EANCode)s,
                        %(NameB2C)s, %(DescriptionShort)s, %(Description)s, %(IsTop)s, %(InfoCode)s, %(WarrantyTerm)s,
                        %(WarrantyUnit)s, %(PartNumber2)s, %(DateAvailible)s, %(DealerPrice1)s, %(Unit)s,
                        %(OnStockCount)s, %(ImgCount)s, %(ImgLastChanged)s, %(ProducerCode)s, %(CategoryCode)s,
                        %(B2C)s, %(B2FPrice)s, %(RCStatus)s, %(RCCode)s, %(IsPremium)s, %(ExtInfoCodes)s)
                    ON DUPLICATE KEY UPDATE
                        Code = VALUES(Code),
                        Name = VALUES(Name),
                        YourPrice = VALUES(YourPrice),
                        YourPriceWithFees = VALUES(YourPriceWithFees),
                        CommodityCode = VALUES(CommodityCode),
                        GarbageFee = VALUES(GarbageFee),
                        AuthorFee = VALUES(AuthorFee),
                        ValuePack = VALUES(ValuePack),
                        ValuePackQty = VALUES(ValuePackQty),
                        Warranty = VALUES(Warranty),
                        CommodityName = VALUES(CommodityName),
                        DealerPrice = VALUES(DealerPrice),
                        EndUserPrice = VALUES(EndUserPrice),
                        Vat = VALUES(Vat),
                        PartNumber = VALUES(PartNumber),
                        OnStock = VALUES(OnStock),
                        OnStockText = VALUES(OnStockText),
                        Status = VALUES(Status),
                        ProducerName = VALUES(ProducerName),
                        RateOfDutyCode = VALUES(RateOfDutyCode),
                        EANCode = VALUES(EANCode),
                        NameB2C = VALUES(NameB2C),
                        DescriptionShort = VALUES(DescriptionShort),
                        Description = VALUES(Description),
                        IsTop = VALUES(IsTop),
                        InfoCode = VALUES(InfoCode),
                        WarrantyTerm = VALUES(WarrantyTerm),
                        WarrantyUnit = VALUES(WarrantyUnit),
                        PartNumber2 = VALUES(PartNumber2),
                        DateAvailible = VALUES(DateAvailible),
                        DealerPrice1 = VALUES(DealerPrice1),
                        Unit = VALUES(Unit),
                        OnStockCount = VALUES(OnStockCount),
                        ImgCount = VALUES(ImgCount),
                        ImgLastChanged = VALUES(ImgLastChanged),
                        ProducerCode = VALUES(ProducerCode),
                        CategoryCode = VALUES(CategoryCode),
                        B2C = VALUES(B2C),
                        B2FPrice = VALUES(B2FPrice),
                        RCStatus = VALUES(RCStatus),
                        RCCode = VALUES(RCCode),
                        IsPremium = VALUES(IsPremium),
                        ExtInfoCodes = VALUES(ExtInfoCodes);
                    """

                    cursor.execute(insert_query, data)
                    connection.commit()

                except Exception as e:
                    log(f"❌ Chyba pri zpracovani produktu: {e}")

        except Exception as e:
            log(f"❌ Chyba pri zpracovani souboru {xml_file}: {e}")

def main():
    connection = connect_db()
    xml_base_dir = 'xml/'
    root_categories = list_categories(xml_base_dir)

    for root_category in root_categories:
        supercategory_dir = os.path.join(xml_base_dir, root_category)
        supercategories = list_categories(supercategory_dir)

        for super_category in supercategories:
            dir_path = os.path.join(supercategory_dir, super_category)
            xml_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.xml')]

            if not xml_files:
                log(f"⚠️ Preskakuji prazdnou slozku: {dir_path}")
                continue

            process_xml_and_save_to_db(xml_files, connection, root_category, super_category)

    connection.close()
    log("✅ Zpracovani dokonceno.")

if __name__ == "__main__":
    main()
