# postgis-seed

One-shot importer **GeoJSON → PostGIS**. Dijalankan oleh service `postgis-seed`
sebelum `geoserver-init`.

## Cara pakai

1. Taruh semua file `.geojson` di `seed/geojson/`.
2. Pastikan nama file (tanpa ekstensi) **sama persis** dengan nama file SLD
   di `init/sld/` — supaya `geoserver-init` otomatis memasang style yang
   benar. Contoh:

   ```
   seed/geojson/X1_KF_1_Kemiringan_Lereng.geojson
   init/sld/X1_KF_1_Kemiringan_Lereng.sld
   ```

   Nama tabel di PostGIS = basename di-lowercase
   (`x1_kf_1_kemiringan_lereng`). Mapping ini sengaja menyamai
   `sld_filename_map()` di `init/init.py`.

3. Rebuild & jalankan:

   ```bash
   docker compose up -d --build postgis-seed geoserver-init
   ```

## Idempotensi

Tabel yang sudah ada **dan berisi baris** akan dilewati. Untuk re-import
paksa (overwrite semua tabel):

```bash
docker compose run --rm -e FORCE=1 postgis-seed
```

## Sumber data

**Sumber kebenaran = shapefile milik maintainer**, dikonversi ke GeoJSON
(shp→geojson) lalu ditaruh manual di `seed/geojson/`. File ini bisa
di-regenerate kapan saja, jadi inilah jalur backup/restore kanonik — tidak ada
DB dump yang perlu dijaga sinkron.

Repo ini sengaja **tidak** menyertakan GeoJSON-nya (`seed/geojson/` gitignored,
±164 MB) — copy file ke folder ini secara manual sesuai kebutuhan deployment.
(Sebagai cadangan, ke-30 file juga masih bisa diambil dari git history repo
`wanantara-green/training-02` pada `3e00032^`, sebelum folder `geojson/`-nya
dihapus — tapi shapefile maintainer adalah sumber hulunya.)
