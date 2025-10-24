from datetime import datetime, timezone
from random import randint
from typing import Literal

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client_3 import InfluxDBClient3, Point

database = "test"
test_url = f"http://localhost:8181"
token = "apiv3_jZmK6lvgwT_F_AiYkKwlG4lEjpo3kObLQidb_kMJ7UQ1DOlCE8JYtZm074_VdYuxzhiH6byw5zn7_iCBCkChAg"


def get_client(
    url=test_url,
    token=token,
    mode: Literal["sync", "async"] = "sync",
    database=database,
):
    return InfluxDBClient3(host=url, token=token, database=database)


def test_insert():
    client: InfluxDBClient3 = get_client(mode="sync")
    for i in range(10):
        client.write(
            record=Point("andy.temperature")
            .field("value", randint(36, 40) + 0.5)
            .tag("id", str(i))
            .tag("source", "体温计")
            .time(datetime.now()),
        )
    client.close()


def test_query():
    client: InfluxDBClient3 = get_client(mode="sync")
    result = client.query(
        'select * from "andy.temperature" where id>5 order by time desc'
    )
    print(result.to_pandas())
    client.close()
