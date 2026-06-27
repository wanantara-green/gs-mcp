"""Skema tool yang dikirim ke DeepSeek (format OpenAI function-calling).

PENTING: ini HANYA 4 tool read-only. Daftar nama yang sama juga di-enforce
ulang sebagai whitelist di mcp_client.py, jadi meski model "berhalusinasi"
memanggil tool lain (delete_resource, create_user, dst.) permintaan itu
ditolak sebelum sampai ke geoserver-mcp.
"""

from __future__ import annotations

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_layers",
            "description": (
                "Daftar layer di GeoServer, opsional difilter per workspace. "
                "Workspace proyek ini adalah 'zonasiluwu'. Pakai tool ini untuk "
                "mengetahui nama layer yang tersedia sebelum query."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Nama workspace, mis. 'zonasiluwu'. Opsional.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_layer_info",
            "description": (
                "Ambil metadata detail sebuah layer (tipe geometri, atribut, "
                "proyeksi/CRS, bounding box, dsb.)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace": {"type": "string", "description": "Workspace pemilik layer, mis. 'zonasiluwu'."},
                    "layer": {"type": "string", "description": "Nama layer."},
                },
                "required": ["workspace", "layer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_features",
            "description": (
                "Query fitur dari layer vektor memakai filter CQL. Mengembalikan "
                "GeoJSON FeatureCollection. Gunakan untuk menghitung/menyaring "
                "fitur berdasarkan atribut (mis. \"luas > 1000\" atau "
                "\"kawasan = 'Permukiman'\")."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "workspace": {"type": "string", "description": "Workspace pemilik layer."},
                    "layer": {"type": "string", "description": "Nama layer yang di-query."},
                    "filter": {
                        "type": "string",
                        "description": "Ekspresi CQL opsional, mis. \"luas_ha > 50\". Kosongkan untuk mengambil semua.",
                    },
                    "properties": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Daftar atribut yang ingin dikembalikan. Opsional.",
                    },
                    "max_features": {
                        "type": "integer",
                        "description": "Batas jumlah fitur (default 10). Naikkan bila perlu menghitung total.",
                    },
                },
                "required": ["workspace", "layer"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_map",
            "description": (
                "Buat URL gambar peta (WMS GetMap) untuk satu atau beberapa layer. "
                "Kembalikan URL yang bisa ditampilkan di peta/HTML."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "layers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Daftar layer format 'workspace:layer', mis. 'zonasiluwu:permukiman'.",
                    },
                    "styles": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Style per layer (opsional, jumlahnya harus sama dengan layers).",
                    },
                    "bbox": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Bounding box [minx, miny, maxx, maxy] dalam EPSG:4326. Opsional.",
                    },
                    "width": {"type": "integer", "description": "Lebar gambar px (default 800)."},
                    "height": {"type": "integer", "description": "Tinggi gambar px (default 600)."},
                    "format": {
                        "type": "string",
                        "enum": ["png", "jpeg", "gif", "tiff", "pdf"],
                        "description": "Format gambar (default png).",
                    },
                },
                "required": ["layers"],
            },
        },
    },
]

# Whitelist nama tool — sumber kebenaran tunggal, dipakai juga oleh mcp_client.
ALLOWED_TOOL_NAMES = {t["function"]["name"] for t in TOOL_SCHEMAS}
