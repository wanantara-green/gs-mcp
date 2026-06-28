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

30 GeoJSON aslinya tersimpan di repo `wanantara-green/training-02` di folder
`geojson/`. Repo ini tidak ikut menyertakan datanya — copy/clone secara manual
sesuai kebutuhan deployment.
