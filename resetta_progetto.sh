#!/bin/bash

# Cancella tutti i file, eccetto "__init__.py", nella directory "visual/migrations"
find visual/migrations -type f ! -name "__init__.py" -exec rm -f {} \;

# Svuota tutte le cartelle nella directory "visual/migrations" (tranne "__init__.py")
find visual/migrations -mindepth 1 -type d -exec rm -rf {} \;

# Cancella il file "db.sqlite3"
rm -f db.sqlite3

echo "Operazione completata: tutti i file eccetto '__init__.py' in visual/migrations sono stati cancellati, e il file 'db.sqlite3' è stato eliminato."