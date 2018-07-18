from logging import INFO, getLogger, StreamHandler
from signal import signal, SIGINT, SIGTERM
from sys import argv
from time import sleep

import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from pythonjsonlogger import jsonlogger

formatter = jsonlogger.JsonFormatter("(asctime) (levelname) (message)", datefmt="%Y-%m-%d %H:%M:%S")

logHandler = StreamHandler()
logHandler.setFormatter(formatter)

log = getLogger(__name__)
log.setLevel(INFO)
log.addHandler(logHandler)


class FakeMetricsCollector:
    def __init__(self, namespace, label_name, label_value, value_http_endpoint):
        self.value = 0
        self.namespace = namespace
        self.label_name = label_name
        self.label_value = label_value
        self.value_http_endpoint = value_http_endpoint

    def collect(self):
        try:
            self.value = float(requests.get(self.value_http_endpoint).content)
        except Exception as ex:
            log.warning(f'Failed to get from {value_http_endpoint}: {ex}')
            self.value = 0

        gauge = GaugeMetricFamily("fake_metric", "This is just for testing HPA", labels=['namespace', label_name])
        gauge.add_metric(value=self.value, labels=[self.namespace, label_value])

        # Remove metrics we've not been able to fetch
        return [gauge]


class SignalHandler:
    def __init__(self):
        self.shutdown = False

        # Register signal handler
        signal(SIGINT, self._on_signal_received)
        signal(SIGTERM, self._on_signal_received)

    def is_shutting_down(self):
        return self.shutdown

    def _on_signal_received(self, _signal, _frame):
        log.info("Exporter is shutting down")
        self.shutdown = True


if __name__ == "__main__":
    # Init logger
    # Register signal handler
    signal_handler = SignalHandler()

    namespace = argv[1]
    label_name = argv[2]
    label_value = argv[3]
    value_http_endpoint = argv[4]

    # Register our custom collector
    log.info("Exporter is starting up")
    REGISTRY.register(FakeMetricsCollector(namespace, label_name, label_value, value_http_endpoint))

    # Start server
    start_http_server(9100)
    log.info(f"Exporter listening on port 9100")

    while not signal_handler.is_shutting_down():
        sleep(1)

    log.info("Exporter has shutdown")
