
# Elinkx Importer (modulární Python datová výměna)

## Autor 
```
Ondrej Zelina 
Tel: +420 721 178 847
email: ondrej.web@gmail.com
```

## Popis
Tento nástroj slouží k importu dat ze SOAP služby Elinkx do MySQL databáze.
Podporuje testovací režim, bezpečné načítání konfigurace z `.env` a rychlé hromadné vkládání pomocí `executemany()`.

## Struktura projektu
```
.
├── main.py
├── config.py
├── db.py
├── importer.py
├── soap_client.py
├── utils.py
├── .env
└── logs/
```

## Spuštění

1. Nainstaluj závislosti:
```bash
pip install mysql-connector-python python-dotenv zeep
nebo použij přikaz pip install -r requirements.txt
```

2. Vytvoř `.env` soubor:
```dotenv
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=heslo123
DB_NAME=test1

SOAP_LOGIN=tvuj@email.cz
SOAP_PASSWORD=tvoje_heslo
WSDL_URL=https://private-ws-cz.elinkx.biz/service.asmx?wsdl
TEST_MODE=false
```

3. Spusť import:
```bash
python main.py
```

[//]: # (4. Pro testovací režim:)

[//]: # (Nastav `TEST_MODE=true` v `.env` a spustí se s mock daty místo skutečného volání SOAP API.)

## Autor 
```
Ondrej Zelina 
Tel: +420 721 178 847
email: ondrej.web@gmail.com
```