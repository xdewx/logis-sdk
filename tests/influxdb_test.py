from datetime import datetime, timezone
from pathlib import Path
from random import randint
from typing import Literal

from influxdb_client.client.influxdb_client import InfluxDBClient
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client_3 import InfluxDBClient3, Point

from logis.metric.influxdb import InfluxCommand

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


def test_command():
    bin_dir = Path("D:\\app\\influxdb3-core-3.5.0-windows_amd64")
    command = InfluxCommand(bin_dir)
    token = command.generate_admin_token(
        offline=False, path=bin_dir / "admin_token.json"
    )
    print("Process exited with code:", token)

    token = command.generate_admin_token(
        offline=True, path=bin_dir / "admin_token.json"
    )
    print("Process exited with code:", token)


def test_serve():
    bin_dir = Path("D:\\app\\influxdb3-core-3.5.0-windows_amd64")
    command = InfluxCommand(bin_dir)
    p = command.serve(
        data_dir=bin_dir / "data",
        object_store="file",
    )
    print(p)
