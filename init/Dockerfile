# geoserver-init — provisioner katalog GeoServer (idempotent, self-healing).
#
# init.py di-COPY ke dalam image, BUKAN bind-mount. Di Coolify, build context
# relatif (./init) berfungsi, sedangkan bind-mount volume relatif (./init:/init)
# tidak ter-mount (file tidak ketemu → "can't open /init/init.py"). Mem-bake
# script ke image membuat self-healing benar-benar jalan tiap deploy.
#
# init.py hanya memakai stdlib (urllib), jadi base image polos sudah cukup.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /init
COPY init.py /init/init.py

CMD ["python", "/init/init.py"]
