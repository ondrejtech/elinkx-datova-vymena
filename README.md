# SOAP datová výměna

**Popis:** Tento projekt slouží k automatické datové výměně s ELINKX systémem pomocí SOAP rozhraní. Načítá produktová data a ukládá je do lokální databáze. Vhodné pro e-shopy, které potřebují pravidelně synchronizovat sortiment.

**Kontakt na správce projektu:**  
Ondřej Zelina  
Tel: +420 721 178 847  
Email: ondrej.web@gmail.com

## Obsah projektu

```
.
├── .env                                                                    # Konfigurace prostředí
├── run.sh                                                                  # Spouštěcí skript
├── requirements.txt                                                        # Python závislosti
├── config.py                                                               # Načítání konfigurace
├── db.py                                                                   # Práce s databází
├── soap_client.py                                                          # SOAP komunikace
├── importer.py                                                             # Hlavní import logika
├── productImporter.py                                                      # Import produktů
├── productNavigatorImporter.py                                             # Import kategorií a filtrů
├── productImageImporter.py                                                 # Import obrázků
├── productLogisticImporter.py                                              # Import logistických dat
├── getProductCatalogueFullNavFilterSOAPDownloadXML.py                      # Stahování XML
├── logs/                                                                   # XML odpovědi a logy
└── README.md                                                               # Tato dokumentace
```

## Požadavky

- Python 3.9+
- MySQL server
- Linux server (např. Ubuntu, AlmaLinux)

## Instalace

1. Klonuj repozitář nebo rozbal ZIP
2. Vytvoř Python virtuální prostředí:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Nainstaluj závislosti:
   ```bash
   pip install -r requirements.txt
   ```
4. Vytvoř `.env` soubor (viz příklad níže)

## .env konfigurace (příklad)

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=elinkx
DB_USER=root
DB_PASSWORD=heslo

SOAP_LOGIN=uzivatel
SOAP_PASSWORD=heslo
SOAP_URL=https://private-ws-cz.elinkx.biz/ws/
```

## Lokální spuštění

```bash
chmod +x run.sh
./run.sh
```

## Automatizace pomocí cron

Otevři crontab:
```bash
crontab -e
```

Přidej záznam:
```
30 6 * * * /cesta/k/projektu/run.sh >> /var/log/elinkx_cron.log 2>&1
00 21 * * * /cesta/k/projektu/run.sh >> /var/log/elinkx_cron.log 2>&1
```

## Nasazení na server

1. Nahraj projekt (např. pomocí scp nebo git)
2. Vytvoř MySQL databázi a nastav `.env`
3. Nastav cron podle části výše
4. Zajisti práva ke složce `logs/`
5. Nastav logrotate nebo dohled (volitelné)

## Stručný popis logiky

- `run.sh` spustí `main.py`, který postupně provede:
  - SOAP dotaz pro stažení dat
  - Zpracování a validaci odpovědí
  - Uložení produktů, kategorií, logistiky a obrázků do databáze

## Logy a debug

Logy najdeš ve složce `logs/`:
- `.log` – hlavní chybové a debug informace
- `.xml` – odpovědi ze SOAP serveru pro ladění
- `missing_attribute.csv` – chybějící data při importu

## Známé problémy & Řešení

- **Timeout SOAP serveru** – zkus znovu za minutu
- **Duplicate entry v databázi** – skript částečně řeší pomocí UPDATE při vkládání
- **Chybějící nebo chybný `.env`** – zkontroluj syntax a proměnné

## Pro koho je určeno

- **Vývojáři**: snadné upravy logiky importu
- **Junior administrátor**: jednoduché nasazení a monitoring
- **Zákazník**: nemusí rozumět kódu, import probíhá automaticky

---

Pro jakékoliv dotazy nebo rozšíření kontaktuj správce projektu:  
**Ondřej Zelina**  
Tel: +420 721 178 847  
Email: ondrej.web@gmail.com

---

> Vytvořeno s ohledem na spolehlivost, jednoduchost a rozšiřitelnost.
