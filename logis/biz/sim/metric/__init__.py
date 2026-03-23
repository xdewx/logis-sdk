from typing import Tuple

from prometheus_client import CollectorRegistry
from prometheus_client import push_to_gateway as _push_to_gateway

from .model import *

PROM_URL = "http://promethous.logis.com"
PROM_GATEWAY_URL = "http://prom-gateway.logis.com"
registry = CollectorRegistry()


def push_to_prometheus(job: str, **kwargs):
    return _push_to_gateway(PROM_GATEWAY_URL, job=job, registry=registry, **kwargs)


from influxdb_client.client.exceptions import InfluxDBError


class BatchingCallback(object):

    def success(self, conf: Tuple[str, str, str], data: str):
        print(f"Written batch: {conf}, data: {data}")

    def error(self, conf: Tuple[str, str, str], data: str, exception: InfluxDBError):
        print(f"Cannot write batch: {conf}, data: {data} due: {exception}")

    def retry(self, conf: Tuple[str, str, str], data: str, exception: InfluxDBError):
        print(
            f"Retryable error occurs for batch: {conf}, data: {data} retry: {exception}"
        )


callback = BatchingCallback()
