# PostGIS seed — one-shot importer GeoJSON -> PostGIS.
# Dipakai sekali setiap deploy. Idempoten: tabel yang sudah ada & berisi data
# di-skip. ogr2ogr (GDAL) dipakai untuk reproyeksi ke EPSG:4326 + buat geom
# index otomatis. psql-client dipakai untuk cek keberadaan tabel.
FROM ghcr.io/osgeo/gdal:alpine-small-latest

RUN apk add --no-cache postgresql-client

WORKDIR /seed
COPY seed.sh /seed/seed.sh
COPY geojson /seed/geojson
RUN chmod +x /seed/seed.sh

CMD ["/seed/seed.sh"]
