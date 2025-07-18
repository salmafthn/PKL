#!/bin/bash
# wait-for-db.sh (Versi 2.0 - Super Smart)

set -e

host="$1"
shift
cmd="$@"

# Loop sampai kita bisa menjalankan query dan menemukan tabel 'prereq'
# Ini memastikan DDL dan DML sudah selesai dijalankan.
for i in {1..24}; do # Kita beri waktu lebih lama (24 * 5s = 2 menit)
  # -Ns me-nonaktifkan header kolom dan output tabular, -e mengeksekusi query
  result=$(mysql -h"$host" -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -Nse "SHOW TABLES LIKE 'prereq';" 2>/dev/null)
  
  if [ "$result" == "prereq" ]; then
    echo "✅ Database is fully initialized and table 'prereq' is found!"
    exec $cmd
  fi
  
  echo "⏳ Database is up, but still initializing... waiting for tables to be created (attempt $i/24)..."
  sleep 5
done

echo "❌ Database did not initialize correctly after 2 minutes. Check MySQL logs for errors in DDL/DML scripts."
exit 1