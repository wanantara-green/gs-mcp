#!/bin/sh
# Import semua *.geojson di /seed/geojson ke PostGIS.
#
# Kontrak:
#   - Nama tabel = basename file di-lowercase (tanpa ekstensi). Ini SENGAJA
#     menyamai mapping di init/init.py:148-151 (sld_filename_map) supaya
#     geoserver-init bisa otomatis pasang SLD <table>.sld ke layer-nya.
#   - Idempoten: tabel yang sudah ada & berisi baris dilewati. Hapus tabel
#     manual (atau set FORCE=1) untuk re-import.
#   - Reproyeksi ke EPSG:4326, kolom geometri "geom". PK dibuat otomatis oleh
#     ogr2ogr sebagai "ogc_fid" — JANGAN paksa FID dari properti "id" GeoJSON,
#     beberapa file punya id duplikat / tipe non-integer dan akan gagal PK.
set -eu

PGHOST="${PG_HOST:-postgis}"
PGPORT="${PG_PORT:-5432}"
PGDB="${PG_DB:-geoserver}"
PGUSER="${PG_USER:-geoserver}"
PGPASS="${PG_PASS:-geoserver}"
SEED_DIR="${SEED_DIR:-/seed/geojson}"
FORCE="${FORCE:-0}"

export PGPASSWORD="$PGPASS"

echo "[seed] menunggu PostGIS ${PGHOST}:${PGPORT} ..."
i=0
until pg_isready -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" >/dev/null 2>&1; do
  i=$((i+1))
  if [ "$i" -gt 60 ]; then
    echo "[seed] FATAL: PostGIS tidak siap setelah 120s."
    exit 1
  fi
  sleep 2
done
echo "[seed] PostGIS siap."

files=$(find "$SEED_DIR" -maxdepth 1 -type f -name '*.geojson' 2>/dev/null | sort || true)
if [ -z "$files" ]; then
  echo "[seed] WARN: tidak ada *.geojson di ${SEED_DIR}; skip (taruh file lalu rebuild)."
  exit 0
fi

total=0; imported=0; skipped=0; failed=0
for f in $files; do
  total=$((total+1))
  base=$(basename "$f" .geojson)
  tbl=$(echo "$base" | tr '[:upper:]' '[:lower:]')

  if [ "$FORCE" != "1" ]; then
    exists=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" -tAc \
      "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='${tbl}'" || true)
    if [ "$exists" = "1" ]; then
      nrows=$(psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDB" -tAc \
        "SELECT count(*) FROM public.\"${tbl}\"" || echo 0)
      if [ "$nrows" -gt 0 ] 2>/dev/null; then
        echo "[seed]   skip   ${tbl}  (sudah ada, ${nrows} baris)"
        skipped=$((skipped+1))
        continue
      fi
    fi
  fi

  echo "[seed]   import ${base} -> ${tbl}"
  if ogr2ogr -f PostgreSQL \
       "PG:host=${PGHOST} port=${PGPORT} dbname=${PGDB} user=${PGUSER} password=${PGPASS}" \
       "$f" \
       -nln "$tbl" -overwrite \
       -lco GEOMETRY_NAME=geom -lco PRECISION=NO \
       -t_srs EPSG:4326; then
    imported=$((imported+1))
  else
    echo "[seed]   GAGAL  ${tbl}"
    failed=$((failed+1))
  fi
done

echo "[seed] selesai: total=${total} import=${imported} skip=${skipped} gagal=${failed}."
[ "$failed" -eq 0 ] || exit 1
