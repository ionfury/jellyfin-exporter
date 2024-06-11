FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt && rm -rf requirements.txt

COPY jellyfin_exporter.py ./jellyfin_exporter.py

CMD ["python", "jellyfin_exporter.py"]

LABEL \
	org.opencontainers.image.title="jellyfin-exporter" \
	org.opencontainers.image.source="https://github.com/ionfury/jellyfin-exporter"