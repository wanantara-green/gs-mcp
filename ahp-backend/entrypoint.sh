#!/bin/sh
set -e
echo "Menunggu PostgreSQL di $POSTGRES_HOST:$POSTGRES_PORT..."
until python -c "import socket,os; s=socket.socket(); s.connect((os.environ['POSTGRES_HOST'], int(os.environ['POSTGRES_PORT']))); s.close()" 2>/dev/null; do
  sleep 1
done
echo "PostgreSQL siap."

# Pastikan database target ada. Di stack GS-MCP, Postgres dipakai bersama
# (db utama "geoserver"); AHP-MCE memakai database terpisah "ahp_mce" pada
# instance yang sama. Django migrate butuh DB sudah ada -> buat bila belum
# (idempoten, via maintenance db "postgres").
python - <<'PY'
import os, psycopg2
from psycopg2 import sql
name = os.environ.get("POSTGRES_DB", "ahp_mce")
conn = psycopg2.connect(dbname="postgres",
    user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"], port=os.environ["POSTGRES_PORT"])
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (name,))
    if cur.fetchone():
        print(f'Database "{name}" sudah ada.')
    else:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
        print(f'Database "{name}" dibuat.')
conn.close()
PY

python manage.py makemigrations kobo_mce --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

if [ "$DJANGO_DEBUG" = "1" ]; then
  echo "Mode pengembangan (runserver)."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "Mode produksi (gunicorn)."
  exec gunicorn ahp_mce.wsgi:application --bind 0.0.0.0:8000 --workers 3
fi
