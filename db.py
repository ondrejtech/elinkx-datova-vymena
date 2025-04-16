import mysql.connector
from config import DB_CONFIG
from utils import log

def connect_to_database():
    return mysql.connector.connect(**DB_CONFIG)

def migrate_tables(connection):
    cursor = connection.cursor()

    tables = {
        "super_categories": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS super_categories;
            CREATE TABLE IF NOT EXISTS super_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                SuperCategoryCode INT NOT NULL UNIQUE,
                SuperCategoryName VARCHAR(255) NOT NULL,
                ParentSuperCategoryCode INT
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "categories": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS categories;
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                CategoryCode INT NOT NULL UNIQUE,
                CategoryName VARCHAR(255) NOT NULL,
                SuperCategoryCode INT,
                ImageList varchar(255),
                FOREIGN KEY (SuperCategoryCode) REFERENCES super_categories(SuperCategoryCode) ON DELETE SET NULL
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "category_attributes": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS category_attributes;
            CREATE TABLE IF NOT EXISTS category_attributes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                AttributeCode INT NOT NULL UNIQUE,
                AttributeName VARCHAR(255) NOT NULL,
                IsPrimary BOOLEAN,
                FilterOperator VARCHAR(100)
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "attribute_values": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS attribute_values;
            CREATE TABLE IF NOT EXISTS attribute_values (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ValueCode INT NOT NULL UNIQUE,
                AttributeCode INT,
                Value VARCHAR(255),
                ValueSort INT,
                FOREIGN KEY (AttributeCode) REFERENCES category_attributes(AttributeCode) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "producers": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS producers;
            CREATE TABLE IF NOT EXISTS producers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ProducerId INT NOT NULL,
                ProducerCode VARCHAR(50) NOT NULL UNIQUE,
                ProducerName VARCHAR(255) NOT NULL
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "commodities": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS commodities;
            CREATE TABLE IF NOT EXISTS commodities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                CommodityCode VARCHAR(50) NOT NULL UNIQUE,
                CommodityName VARCHAR(255) NOT NULL,
                CommodityParentCode VARCHAR(50)
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "product_index_tree1": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS product_index_tree1;
            CREATE TABLE IF NOT EXISTS product_index_tree1 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                IndexCode INT NOT NULL UNIQUE,
                CommodityCode VARCHAR(50),
                IndexName VARCHAR(255),
                IndexSort VARCHAR(50),
                IndexSortCode VARCHAR(50),
                IndexLevel INT,
                IndexOrder INT,
                IndexCodeName VARCHAR(255),
                FOREIGN KEY (CommodityCode) REFERENCES commodities(CommodityCode) ON DELETE SET NULL
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "product_index_items": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS product_index_items;
            CREATE TABLE IF NOT EXISTS product_index_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                RootIndexCode INT,
                ItemIndexCode INT,
                ItemIndexName VARCHAR(255),
                FOREIGN KEY (RootIndexCode) REFERENCES product_index_tree1(IndexCode) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "transportation_list": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS transportation_list;
            CREATE TABLE IF NOT EXISTS transportation_list (
                id INT AUTO_INCREMENT PRIMARY KEY,
                Code INT NOT NULL UNIQUE,
                Name VARCHAR(255) NOT NULL,
                TypeCode TINYINT
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "users": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS users;
            CREATE TABLE IF NOT EXISTS users (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                surname VARCHAR(255) NOT NULL,
                phone VARCHAR(255) NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                note VARCHAR(255) NULL,
                ic VARCHAR(255) NULL,
                dic VARCHAR(255) NULL,
                company_name VARCHAR(255) NULL,
                address VARCHAR(255) NOT NULL,
                city VARCHAR(255) NOT NULL,
                postcode VARCHAR(255) NOT NULL,
                state VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "products": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS products;
            CREATE TABLE IF NOT EXISTS products (
                ProId INT PRIMARY KEY UNIQUE,
                Code VARCHAR(20) NULL,
                Name TEXT,
                YourPrice DECIMAL(10, 2),
                YourPriceWithFees DECIMAL(10, 2),
                CommodityCode TEXT,
                GarbageFee DECIMAL(10, 2),
                AuthorFee DECIMAL(10, 2),
                ValuePack DECIMAL(10, 6),
                ValuePackQty DECIMAL(10, 6),
                Warranty TEXT,
                CommodityName TEXT,
                DealerPrice DECIMAL(10, 2),
                EndUserPrice DECIMAL(10, 2),
                Vat DECIMAL(5, 2),
                PartNumber TEXT,
                OnStock BOOLEAN,
                OnStockText TEXT,
                Status TEXT,
                ProducerName TEXT,
                RateOfDutyCode TEXT,
                EANCode TEXT,
                NameB2C TEXT,
                DescriptionShort TEXT,
                Description LONGTEXT,
                IsTop BOOLEAN,
                InfoCode TEXT,
                WarrantyTerm varchar(50) null,
                WarrantyUnit varchar(50) null,
                PartNumber2 TEXT,
                DateAvailible DATETIME,
                DealerPrice1 DECIMAL(10, 2),
                Unit TEXT,
                OnStockCount DECIMAL(10, 2),
                ImgCount INT,
                ImgLastChanged DATETIME,
                ProducerCode VARCHAR(10),
                CategoryCode INT,
                B2C BOOLEAN,
                B2FPrice DECIMAL(10, 2),
                RCStatus TEXT,
                RCCode TEXT,
                IsPremium BOOLEAN,
                ExtInfoCodes TEXT,
                FOREIGN KEY (CategoryCode) REFERENCES categories(CategoryCode) ON DELETE CASCADE,
                FOREIGN KEY (ProducerCode) REFERENCES producers(ProducerCode) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "product_images": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS product_images;
            CREATE TABLE IF NOT EXISTS product_images (
                ProId INT NOT NULL,
                URL TEXT NOT NULL,
                FOREIGN KEY (ProId) REFERENCES products(ProId) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "product_navigator_data": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS product_navigator_data;
            CREATE TABLE IF NOT EXISTS product_navigator_data (
                ProId INT NOT NULL,
                AttributeCode INT(10) NOT NULL,
                ValueCode INT(10) NOT NULL,
                FOREIGN KEY (ProId) REFERENCES products(ProId) ON DELETE CASCADE,
                FOREIGN KEY (AttributeCode) REFERENCES category_attributes(AttributeCode) ON DELETE CASCADE,
                FOREIGN KEY (ValueCode) REFERENCES attribute_values(ValueCode) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "product_logistic": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS product_logistic;
            CREATE TABLE IF NOT EXISTS product_logistic (
                ProId INT NOT NULL PRIMARY KEY,
                `typ` VARCHAR(20) NOT NULL,
                `count` VARCHAR(20) NOT NULL,
                weight DECIMAL(10,2) NOT NULL,
                length INT(10) NOT NULL,
                width INT(10) NOT NULL,
                height INT(10) NOT NULL,
                FOREIGN KEY (ProId) REFERENCES products(ProId) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "shopping_cart": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS shopping_cart;
            CREATE TABLE IF NOT EXISTS shopping_cart (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                ProId INT NOT NULL,
                user_id INT NOT NULL,
                quantity INT NOT NULL,
                FOREIGN KEY (ProId) REFERENCES products(ProId) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "orders": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS orders;
            CREATE TABLE IF NOT EXISTS orders (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_number INT NOT NULL,
                status VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_order_number (order_number)
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "order_items": """
            SET FOREIGN_KEY_CHECKS = 0;
            DROP TABLE IF EXISTS order_items;
            CREATE TABLE IF NOT EXISTS order_items (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                order_number INT NOT NULL,
                ProId INT NOT NULL,
                quantity INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_number) REFERENCES orders(order_number) ON DELETE CASCADE,
                FOREIGN KEY (ProId) REFERENCES products(ProId) ON DELETE CASCADE
            );
            SET FOREIGN_KEY_CHECKS = 1;
        """,
        "order_items": """
                    SET FOREIGN_KEY_CHECKS = 0;
                    DROP TABLE IF EXISTS invoices;
                    CREATE TABLE IF NOT EXISTS invoices (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        invoice_number varchar(255) NOT NULL,
                        order_number VARCHAR(255) NOT NULL,
                        user_id INT NOT NULL,
                        status varchar(255),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    );
                    SET FOREIGN_KEY_CHECKS = 1;
        """
    }

    for name, ddl in tables.items():
        for statement in ddl.strip().split(';'):
            if statement.strip():
                cursor.execute(statement + ';')
        log(f"🛠️ Tabulka `{name}` pripravena.")
    connection.commit()
