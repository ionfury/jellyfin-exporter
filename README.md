# Jellyfin Exporter

A(nother) Prometheus exporter for Jellyfin.

## Usage

TBD

## Configuration

| Environment Variable | Description | Default | Required |
|-|-|-|:-:|
| JELLYFIN_EXPORTER_API_KEY | The API key to Jellyfin | | ✅ |
| JELLYFIN_EXPORTER_PORT | The port jellyfin-exporter will listen on | 8080 | ❌ |
| JELLYFIN_EXPORTER_URL | The full URL to Jellyfin | localhost:9090 | ❌ |
| JELLYFIN_EXPORTER_INSTANCE_NAME | A unique name for your jellyfin instance | jellyfin | ❌ |