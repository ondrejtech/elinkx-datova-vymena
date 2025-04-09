# importer.py
from soap_client import get_product_categories_image
from utils import log

def insert_super_categories(connection, items):
    cursor = connection.cursor()
    count = 0
    for item in items:
        try:
            cursor.execute("""
                INSERT INTO super_categories (SuperCategoryCode, SuperCategoryName, ParentSuperCategoryCode)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    SuperCategoryName = VALUES(SuperCategoryName),
                    ParentSuperCategoryCode = VALUES(ParentSuperCategoryCode)
            """, (
                item.get("SuperCategoryCode"),
                item.get("SuperCategoryName"),
                item.get("ParentSuperCategoryCode")
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání superkategorie: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} superkategorií.")

def insert_categories(connection, categories, super_category_code):
    cursor = connection.cursor()
    count = 0
    for cat in categories:
        try:
            cursor.execute("""
                INSERT IGNORE INTO categories (CategoryCode, CategoryName, SuperCategoryCode)
                VALUES (%s, %s, %s)
            """, (
                cat.get("CategoryCode"),
                cat.get("CategoryName"),
                super_category_code
            ))
            if cursor.rowcount > 0:
                count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání kategorie: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} nových kategorií.")

def update_category_images(connection):
    log("Aktualizuji obrázky kategorií")
    cursor = connection.cursor()
    updated = 0

    response = get_product_categories_image()
    categories = response.get("ProductCategoryList", {}).get("ProductCategory", [])

    if isinstance(categories, dict):
        categories = [categories]

    for cat in categories:
        category_code = cat.get("CategoryCode")
        image_url = None

        image_list = cat.get("ImageList")
        if image_list and "ProductCategoryImage" in image_list:
            images = image_list["ProductCategoryImage"]
            if isinstance(images, dict):
                images = [images]
            if isinstance(images, list) and len(images) > 0:
                image_url = images[0].get("URL")

        try:
            cursor.execute("""
                UPDATE categories
                SET ImageList = %s
                WHERE CategoryCode = %s
            """, (image_url, category_code))
            if cursor.rowcount > 0:
                updated += 1
        except Exception as e:
            log(f"❌ Chyba při aktualizaci obrázku pro kategorii {category_code}: {e}")

    connection.commit()
    log(f"✅ Aktualizováno {updated} kategorií s novými obrázky.")


def insert_attributes(connection, attributes):
    cursor = connection.cursor()
    count = 0
    for attr in attributes:
        try:
            cursor.execute("""
                INSERT INTO category_attributes (AttributeCode, AttributeName, IsPrimary, FilterOperator)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    AttributeName = VALUES(AttributeName),
                    IsPrimary = VALUES(IsPrimary),
                    FilterOperator = VALUES(FilterOperator)
            """, (
                attr.get("AttributeCode"),
                attr.get("AttributeName"),
                attr.get("IsPrimary"),
                attr.get("FilterOperator")
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání atributu: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} atributů.")

def insert_attribute_values(connection, values):
    cursor = connection.cursor()
    count = 0
    for val in values:
        try:
            cursor.execute("""
                INSERT INTO attribute_values (ValueCode, AttributeCode, Value, ValueSort)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    AttributeCode = VALUES(AttributeCode),
                    Value = VALUES(Value),
                    ValueSort = VALUES(ValueSort)
            """, (
                val.get("ValueCode"),
                val.get("AttributeCode"),
                val.get("Value"),
                val.get("ValueSort")
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání hodnoty atributu: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} hodnot atributů.")

def insert_producers(connection, producers):
    cursor = connection.cursor()
    count = 0
    for item in producers:
        try:
            cursor.execute("""
                INSERT INTO producers (ProducerId, ProducerCode, ProducerName)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    ProducerName = VALUES(ProducerName)
            """, (
                item.get("ProducerId"),
                item.get("ProducerCode"),
                item.get("ProducerName")
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání výrobce: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} výrobců.")

def insert_commodities(connection, data):
    cursor = connection.cursor()
    count = 0
    for item in data:
        if not isinstance(item, dict):
            continue
        try:
            cursor.execute("""
                INSERT INTO commodities (CommodityCode, CommodityName, CommodityParentCode)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    CommodityName = VALUES(CommodityName),
                    CommodityParentCode = VALUES(CommodityParentCode);
            """, (
                item.get('CommodityCode'),
                item.get('CommodityName'),
                item.get('CommodityParentCode')
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání komodity: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} komodit.")

def insert_product_index(connection, index_items):
    cursor = connection.cursor()
    count = 0
    for item in index_items:
        try:
            cursor.execute("""
                INSERT INTO product_index_tree1 (
                    IndexCode, CommodityCode, IndexName,
                    IndexSort, IndexSortCode, IndexLevel,
                    IndexOrder, IndexCodeName
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    CommodityCode = VALUES(CommodityCode),
                    IndexName = VALUES(IndexName),
                    IndexSort = VALUES(IndexSort),
                    IndexSortCode = VALUES(IndexSortCode),
                    IndexLevel = VALUES(IndexLevel),
                    IndexOrder = VALUES(IndexOrder),
                    IndexCodeName = VALUES(IndexCodeName)
            """, (
                item.get("IndexCode"),
                item.get("CommodityCode"),
                item.get("IndexName"),
                item.get("IndexSort"),
                item.get("IndexSortCode"),
                item.get("IndexLevel"),
                item.get("IndexOrder"),
                item.get("IndexCodeName")
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání product index: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} záznamů v product_index_tree1.")

def insert_product_index_items(connection, root_code, items):
    def process_items(parent_code, items):
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            return

        cursor = connection.cursor()
        for item in items:
            try:
                index_code = item.get("IndexCode")
                index_name = item.get("IndexName")
                if index_code and index_name:
                    cursor.execute("""
                        INSERT INTO product_index_items (
                            RootIndexCode, ItemIndexCode, ItemIndexName
                        ) VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            ItemIndexName = VALUES(ItemIndexName)
                    """, (
                        parent_code,
                        index_code,
                        index_name
                    ))
                children = item.get("ProductIndexList")
                if children and isinstance(children, dict):
                    child_items = children.get("ProductIndexItem")
                    if child_items:
                        process_items(index_code, child_items)
            except Exception as e:
                log(f"❌ Chyba při ukládání product_index_items: {e}")
        connection.commit()

    if items and isinstance(items, dict):
        process_items(root_code, items.get("ProductIndexItem"))
    elif isinstance(items, list):
        for item in items:
            process_items(root_code, item.get("ProductIndexItem"))

    log("✅ Rekurzivní import product_index_items byl dokončen.")

def insert_transportation_list(connection, items):
    cursor = connection.cursor()
    count = 0
    if not isinstance(items, list):
        items = [items]
    for item in items:
        try:
            cursor.execute("""
                INSERT INTO transportation_list (Code, Name, TypeCode)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Name = VALUES(Name),
                    TypeCode = VALUES(TypeCode)
            """, (
                item.get("Code"),
                item.get("Name"),
                item.get("TypeCode")
            ))
            count += 1
        except Exception as e:
            log(f"❌ Chyba při ukládání transportation_list: {e}")
    connection.commit()
    log(f"✅ Uloženo {count} záznamů v transportation_list.")
