import pytest
import httpx
from time import sleep

from pykli.ksqldb import KsqlDBClient

@pytest.fixture(scope="module")
def ksqldb_url():
    return "http://localhost:28088"


@pytest.fixture(scope="module")
def ksqldb(ksqldb_url):
    ksqldb = KsqlDBClient(ksqldb_url)
    for i in range(5):
        try:
            ksqldb.stmt("""
drop stream if exists pykli_stream_json delete topic;
drop type if exists pykli_type;
drop connector if exists pykli_connector;
""")
            return ksqldb
        except httpx.HTTPError:
            print(f"Waiting for KsqlDB #{i}, {i * 10} sec")
            sleep(10)
    raise RuntimeError(f"{ksqldb_url} unavailable")


def list_type_names(ksqldb) -> list[str]:
    json = ksqldb.stmt("show types;")[0]
    return json["types"].keys()


def list_topic_names(ksqldb) -> list[str]:
    json = ksqldb.stmt("show topics;")[0]
    return [t["name"] for t in json["topics"]]


def list_stream_names(ksqldb) -> list[str]:
    json = ksqldb.stmt("show streams;")[0]
    return [t["name"] for t in json["streams"]]



def list_table_names(ksqldb) -> list[str]:
    json = ksqldb.stmt("show tables;")[0]
    return [t["name"] for t in json["tables"]]


def list_connector_names(ksqldb) -> list[str]:
    json = ksqldb.stmt("show connectors;")[0]
    return [t["name"] for t in json["connectors"]]


