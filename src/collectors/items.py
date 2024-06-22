from prometheus_client.core import GaugeMetricFamily
import traceback


class JellyfinItems(object):
    def __init__(self, request_api, critical_logger):
        self.request_api = request_api
        self.critical_logger = critical_logger

    def collect(self):
        endpoint = "/Items/Counts"
        try:
            data = self.request_api(endpoint)
            yield self.count(data)
        except Exception as ex:
            self.critical_logger(f"Error collecting {endpoint}: %s", ex)
            self.critical_logger("Traceback: %s", traceback.format_exc())

    def count(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_items",
            "Number of jellyfin items.",
            labels=["type"],
        )
        for item, value in data.items():
            gauge.add_metric([item], int(value))

        return gauge
