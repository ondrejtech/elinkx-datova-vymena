# importer.py
from utils import log
import mysql.connector
from dotenv import load_dotenv
import os

# Načti .env soubor
load_dotenv()

def connect():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def add_background_column(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("ALTER TABLE super_categories ADD COLUMN background TEXT;")
        connection.commit()
        log("✅ Sloupec 'background' byl úspěšně přidán do super_categories.")
    except Exception as e:
        log(f"❌ Chyba při přidávání sloupce 'background': {e}")

def update_backgrounds(connection):
    cursor = connection.cursor()

    updates = [
        ("--it-products", 52),
        ("--electronics", 53),
        ("--small-appliances", 54),
        ("--large-appliances", 55),
        ("--sport-outdoor", 56),
        ("--house-garden", 57),
        ("--body-care", 58)
    ]

    updated = 0
    for background, code in updates:
        try:
            cursor.execute("""
                           UPDATE super_categories
                           SET background = %s
                           WHERE SuperCategoryCode = %s
                           """, (background, code))
            updated += cursor.rowcount
        except Exception as e:
            log(f"❌ Chyba při aktualizaci background pro kód {code}: {e}")

    connection.commit()
    log(f"✅ Úspěšně aktualizováno {updated} řádků v super_categories.")

if __name__ == "__main__":
    try:
        conn = connect()
        add_background_column(conn)
        update_backgrounds(conn)
        conn.close()
        log("✅ Skript byl úspěšně dokončen.")
    except Exception as e:
        log(f"❌ Skript selhal: {e}")