#!/bin/bash
# wait-for-db.sh (Versi 2.0 - Super Smart)

set -e

host="$1"
shift
cmd="$@"

for i in {1..24}; do 
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