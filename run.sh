#!/bin/bash

# smazani slozky xml a jeji znovu vytvoreni  
rm -rf ./xml
mkdir ./xml

# Aktivuj virtuální prostředí
source .venv/bin/activate

# Vytvoř timestamp pro zálohu
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_file="backup/elinkx_backup_$timestamp.sql"
echo "🗃️ Zálohuji databázi do $backup_file..."
mkdir -p backup
mysqldump -u root -pZelio_6236 elinkx > "$backup_file"

echo "✅ Starting fully automated import..."

# Automatická odpověď na všechny vstupy (včetně výběru kategorie)
python -m automatization.auto_main <<EOF
y
y
0
y
EOF
python3 alter_table.py

echo "🎉 Hotovo."
