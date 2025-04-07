from db import connect_to_database, migrate_tables
from getProductCatalogueFullNavFilterSOAPDownloadXML import getProductCatalogueFullNavFilterSOAPDownload

from soap_client import (
    get_navigator_data, get_product_producers, get_commodities,
    get_product_index, get_transportation
)
from importer import (
    insert_producers, insert_super_categories, insert_categories,
    insert_attributes, insert_attribute_values, insert_commodities,
    insert_product_index, insert_product_index_items, insert_transportation_list
)
from utils import log

def run():
    try:
        import_database = input('Do you want to start importing the database? (y/n)')
        if(import_database == 'y'):
            log("📡 Spouštím import dat ze služby Elinkx...")

            connection = connect_to_database()
            migrate_tables(connection)

            # Načtení hlavních dat
            data = get_navigator_data()

            log("🧩 Import superkategorií")
            super_categories = data.get("ProductSuperCategoryList", {}).get("ProductSuperCategory", [])
            insert_super_categories(connection, super_categories)

            for super_cat in super_categories:
                super_code = super_cat.get("SuperCategoryCode")
                cat_list = super_cat.get("ProductCategoryList")
                if isinstance(cat_list, dict):
                    categories = cat_list.get("ProductCategory", [])
                    if isinstance(categories, dict):
                        categories = [categories]
                    insert_categories(connection, categories, super_code)

            log("🧩 Import atributů")
            insert_attributes(connection,
                              data.get("ProductCategoryAttributeList", {}).get("ProductCategoryAttribute", []))

            attr_values_raw = data.get("ProductCategoryAttributeValueList", {}).get("ProductCategoryAttributeValue", [])
            if isinstance(attr_values_raw, dict):
                attr_values_raw = [attr_values_raw]
            insert_attribute_values(connection, attr_values_raw)

            # Výrobci
            producers_data = get_product_producers()
            insert_producers(connection, producers_data.get("ProductProducerList", {}).get("ProductProducer", []))

            # Komodity
            commodities_data = get_commodities()
            insert_commodities(connection, commodities_data.get("ProductCommodityList", {}).get("ProductCommodity", []))

            # Strom indexu
            index_data = get_product_index()
            product_index_root = index_data.get("ProductIndexRoot")
            if product_index_root:
                insert_product_index(connection, [product_index_root])
                insert_product_index_items(
                    connection,
                    product_index_root.get("IndexCode"),
                    product_index_root.get("ProductIndexList")
                )

            # Doprava
            trans_data = get_transportation()
            trans_list = trans_data.get("TransportationList", {}).get("Transportation")
            if trans_list:
                insert_transportation_list(connection, trans_list)

        # Nacteni XML Katalogu
        downloadCatalogue = input('Do you want to download the XML catalogue? (y/n): ')
        if (downloadCatalogue == 'y'):
            getProductCatalogueFullNavFilterSOAPDownload()

        if 'connection' in locals():
            connection.close()

        log("✅ Import dokončen. Spojení s databází bylo uzavřeno.")

    except Exception as e:
        log(f"❌ Kritická chyba: {e}")


if __name__ == "__main__":
    run()
