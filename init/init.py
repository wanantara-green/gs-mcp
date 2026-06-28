#!/usr/bin/env python3
"""
GeoServer auto-provisioner (idempotent, self-healing).

Dijalankan oleh service `geoserver-init` setiap kali stack deploy.
Tujuan: memastikan katalog GeoServer (workspace + datastore PostGIS +
featuretype/layer + SLD style) SELALU ada — walau volume data GeoServer
ter-reset saat redeploy. Data spasial mentah tetap berada di PostGIS.

- Jika katalog sudah lengkap  -> langsung exit 0 (skip).
- Jika hilang / belum ada     -> dibangun ulang otomatis dari tabel PostGIS.

Hanya pakai stdlib (urllib) supaya base image tidak perlu dependency tambahan.
"""
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# ── Konfigurasi (override via environment) ───────────────────────────
GS    = os.environ.get("GEOSERVER_URL", "http://geoserver:8080/geoserver").rstrip("/") + "/rest"
USER  = os.environ.get("GEOSERVER_USER", "admin")
PASS  = os.environ.get("GEOSERVER_PASSWORD", "geoserver")
WS    = os.environ.get("GEOSERVER_WORKSPACE", "zonasiluwu")
DS    = os.environ.get("GEOSERVER_DATASTORE", "zonasiluwu_pg")

PG_HOST = os.environ.get("PG_HOST", "postgis")
PG_PORT = os.environ.get("PG_PORT", "5432")
PG_DB   = os.environ.get("PG_DB",   "geoserver")
PG_USER = os.environ.get("PG_USER", "geoserver")
PG_PASS = os.environ.get("PG_PASS", "geoserver")
PG_SCHEMA = os.environ.get("PG_SCHEMA", "public")

# Sumber file SLD: folder LOKAL yang di-bake ke image (init/sld) — dulu ditarik
# dari raw.githubusercontent training-02, kini dipindah ke repo ini agar tak ada
# dependensi lintas-repo/jaringan & training-02 tak perlu menyimpan SLD lagi.
SLD_DIR = os.environ.get(
    "SLD_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "sld"),
)

_AUTH = "Basic " + base64.b64encode(f"{USER}:{PASS}".encode()).decode()


def req(method, path, data=None, ctype="application/json", base=GS, raw_url=None):
    url = raw_url if raw_url else base + path
    headers = {"Accept": "application/json"}
    body = None
    if raw_url is None:
        headers["Authorization"] = _AUTH
    if data is not None:
        headers["Content-Type"] = ctype
        body = data.encode("utf-8") if isinstance(data, str) else data
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return 0, str(e)


def wait_for_geoserver(timeout=300):
    print("[init] menunggu GeoServer siap ...", flush=True)
    deadline = time.time() + timeout
    while time.time() < deadline:
        code, _ = req("GET", "/about/version.json")
        if code == 200:
            print("[init] GeoServer siap.", flush=True)
            return True
        time.sleep(5)
    print("[init] FATAL: GeoServer tidak siap dalam batas waktu.", flush=True)
    return False


def ensure_workspace():
    code, _ = req("GET", f"/workspaces/{WS}.json")
    if code == 200:
        print(f"[init] workspace '{WS}' sudah ada.", flush=True)
        return
    code, body = req("POST", "/workspaces",
                     json.dumps({"workspace": {"name": WS}}))
    print(f"[init] buat workspace '{WS}' -> {code}", flush=True)


def ensure_datastore():
    code, _ = req("GET", f"/workspaces/{WS}/datastores/{DS}.json")
    if code == 200:
        print(f"[init] datastore '{DS}' sudah ada.", flush=True)
        return
    payload = {
        "dataStore": {
            "name": DS,
            "connectionParameters": {"entry": [
                {"@key": "host", "$": PG_HOST},
                {"@key": "port", "$": PG_PORT},
                {"@key": "database", "$": PG_DB},
                {"@key": "user", "$": PG_USER},
                {"@key": "passwd", "$": PG_PASS},
                {"@key": "dbtype", "$": "postgis"},
                {"@key": "schema", "$": PG_SCHEMA},
                {"@key": "Expose primary keys", "$": "true"},
            ]}
        }
    }
    code, body = req("POST", f"/workspaces/{WS}/datastores",
                     json.dumps(payload))
    print(f"[init] buat datastore '{DS}' -> {code}", flush=True)


def _list(body, key):
    try:
        v = json.loads(body)[key]
        if v == "":
            return []
        inner = next(iter(v.values()))
        if isinstance(inner, list):
            return inner
        return [inner]
    except Exception:  # noqa: BLE001
        return []


def available_tables():
    code, body = req("GET",
                     f"/workspaces/{WS}/datastores/{DS}/featuretypes.json?list=available")
    try:
        return json.loads(body)["list"]["string"]
    except Exception:  # noqa: BLE001
        return []


def published_featuretypes():
    code, body = req("GET",
                     f"/workspaces/{WS}/datastores/{DS}/featuretypes.json")
    names = []
    for ft in _list(body, "featureTypes"):
        if isinstance(ft, dict) and "name" in ft:
            names.append(ft["name"])
    return names


def sld_filename_map():
    try:
        return {fn[:-4].lower(): fn
                for fn in os.listdir(SLD_DIR) if fn.endswith(".sld")}
    except Exception as e:  # noqa: BLE001
        print(f"[init] WARN: gagal baca folder SLD {SLD_DIR} ({e}); SLD dilewati.",
              flush=True)
        return {}


def publish_featuretype(table):
    payload = {"featureType": {"name": table, "srs": "EPSG:4326"}}
    code, body = req("POST",
                     f"/workspaces/{WS}/datastores/{DS}/featuretypes",
                     json.dumps(payload))
    return code


def upload_style(table, filename):
    try:
        with open(os.path.join(SLD_DIR, filename), "r", encoding="utf-8") as f:
            sld = f.read()
    except Exception:  # noqa: BLE001
        return None
    # Deklarasi versi SLD pada file = 1.1.0 tapi isi memakai konstruk SLD 1.0
    # (CssParameter / ogc:Filter). Selaraskan agar parser 1.0 menerima.
    sld = sld.replace('version="1.1.0"', 'version="1.0.0"')
    sld = sld.replace('sld/1.1.0/StyledLayerDescriptor.xsd',
                      'sld/1.0.0/StyledLayerDescriptor.xsd')
    req("DELETE", f"/workspaces/{WS}/styles/{table}?recurse=true&purge=true")
    code, _ = req("POST", f"/workspaces/{WS}/styles?name={table}",
                  sld, ctype="application/vnd.ogc.sld+xml")
    if code == 201:
        req("PUT", f"/layers/{WS}:{table}",
            json.dumps({"layer": {"defaultStyle":
                       {"name": f"{WS}:{table}", "workspace": WS}}}))
    return code


def main():
    if not wait_for_geoserver():
        sys.exit(1)

    ensure_workspace()
    ensure_datastore()

    # `list=available` hanya memuat tabel yang BELUM dipublish; yang sudah
    # dipublish pindah ke daftar featuretype. Target = gabungan keduanya.
    already = set(published_featuretypes())
    tables = sorted(set(available_tables()) | already)
    if not tables:
        print("[init] WARN: tidak ada tabel di PostGIS — tidak ada yang dipublish.",
              flush=True)
        sys.exit(0)

    if already.issuperset(set(tables)):
        print(f"[init] katalog sudah lengkap ({len(already)} layer). Skip.",
              flush=True)
        sys.exit(0)

    print(f"[init] memprovisi {len(tables)} layer ...", flush=True)
    sld_map = sld_filename_map()
    pub_ok = sty_ok = 0
    for t in tables:
        if t in already:
            pub_ok += 1
        else:
            c = publish_featuretype(t)
            if c == 201:
                pub_ok += 1
            else:
                print(f"[init]   publish {t} -> {c}", flush=True)
                continue
        fn = sld_map.get(t)
        if fn:
            sc = upload_style(t, fn)
            if sc == 201:
                sty_ok += 1
    print(f"[init] selesai: featuretype {pub_ok}/{len(tables)}, "
          f"style {sty_ok}/{len(tables)}.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
