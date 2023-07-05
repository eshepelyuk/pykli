from pprint import pformat, pprint
import pytest
import httpx
from time import sleep
from click.testing import CliRunner
from pykli.ksqldb import KsqlDBClient
from pykli.__main__ import main

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput


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


@pytest.fixture(scope="function")
def mock_input():
    with create_pipe_input() as pipe_input:
        with create_app_session(input=pipe_input, output=DummyOutput()):
            yield pipe_input


@pytest.mark.e2e
def test_streams(mock_input, ksqldb):

    mock_input.send_text("""
create or replace stream pykli_stream_json (
    id varchar key, `firstName` varchar, "Age" int
) with (kafka_topic = 'pykli_stream_json', partitions = 1, value_format = 'json');
describe pykli_stream_json;
show streams;
show topics;

insert into pykli_stream_json (id, `firstName`, `Age`) values ('uuid1', 'Tom', 20);
insert into pykli_stream_json (id, `firstName`, `Age`) values ('uuid2', 'Fred', 30);

select * from pykli_stream_json where `firstName` = 'Tom';
select * from pykli_stream_json where `Age` > 20;

exit;
""")

    runner = CliRunner()
    r = runner.invoke(main, [ksqldb.url])
    output = r.output.split("\n")

    assert r.exit_code == 0
    assert "Stream created" in output
    assert "| Stream Name         | Kafka Topic                 | Key Format | Value Format | Windowed |" in output
    assert "| PYKLI_STREAM_JSON   | pykli_stream_json           | KAFKA      | JSON         | False    |" in output
    assert output.count("| ID    | firstName | Age |") == 2
    assert output.count("| uuid1 | Tom       |  20 |") == 1
    assert output.count("| uuid2 | Fred      |  30 |") == 1

    assert "| Kafka Topic                 | Partitions | Partition Replicas |" in output
    assert "| pykli_stream_json           |          1 |                  1 |" in output

    assert "pykli_stream_json" in ksqldb.list_topic_names()
    assert "PYKLI_STREAM_JSON" in ksqldb.list_stream_names()

    mock_input.send_text("""
drop stream pykli_stream_json delete topic;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Source `PYKLI_STREAM_JSON` (topic: pykli_stream_json) was dropped." in r.output

    assert "pykli_stream_json" not in ksqldb.list_topic_names()
    assert "PYKLI_STREAM_JSON" not in ksqldb.list_stream_names()


@pytest.mark.e2e
def test_types(mock_input, ksqldb):
    mock_input.send_text("""
create type pykli_type as STRUCT<name VARCHAR, age INT>;
show types;
exit;
""")

    runner = CliRunner()
    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Registered custom type with name 'PYKLI_TYPE'" in r.output
    assert "PYKLI_TYPE" in ksqldb.list_type_names()

    mock_input.send_text("""
drop type if exists pykli_type;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Dropped type 'PYKLI_TYPE'" in r.output
    assert "PYKLI_TYPE" not in ksqldb.list_type_names()


@pytest.mark.e2e
def test_functions(mock_input, ksqldb):
    mock_input.send_text("""
show functions;
describe function TO_JSON_STRING;
exit;
""")

    runner = CliRunner()
    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "| Function Name         | Category           |" in r.output
    assert "| TO_JSON_STRING        | JSON               |" in r.output
    assert "[ Function Overview ]" in r.output
    assert "Jar         | internal" in r.output
    assert "| Signature               | Returns | Description |" in r.output


@pytest.mark.e2e
def test_connectors(mock_input, ksqldb):
    mock_input.send_text("""
create sink connector pykli_connector with (
    "connector.class"='org.apache.kafka.connect.tools.MockSinkConnector',
    "topics"='pykli_connector'
);
show topics;
show connectors;
describe connector pykli_connector;
exit;
""")

    runner = CliRunner()
    r = runner.invoke(main, [ksqldb.url], terminal_width=240)

    assert r.exit_code == 0
    assert "Created connector PYKLI_CONNECTOR" in r.output

    assert "| Connector Name  | Type | Class" in r.output
    assert "| PYKLI_CONNECTOR | sink | org.apache.kafka.connect.tools.MockSinkConnector" in r.output

    assert "[ Connector Overview ]" in r.output
    assert "Class    | org.apache.kafka.connect.tools.MockSinkConnector" in r.output

    assert "Task ID" in r.output
    assert "RUNNING" in r.output

    assert "PYKLI_CONNECTOR" in ksqldb.list_connector_names()
    assert "pykli_connector" in ksqldb.list_topic_names()

    mock_input.send_text("""
drop connector if exists pykli_connector;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])
    assert r.exit_code == 0
    assert "PYKLI_CONNECTOR" not in ksqldb.list_connector_names()


@pytest.mark.skip
@pytest.mark.e2e
def test_tables(mock_input, ksqldb):
    mock_input.send_text("""
create or replace stream pykli_json (
  id varchar key, `firstName` varchar, "Age" int
) with (kafka_topic = 'pykli_json', partitions = 1, value_format = 'json');

insert into pykli_json (id, `firstName`, `Age`) values ('uuid1', 'Tom', 20);
insert into pykli_json (id, `firstName`, `Age`) values ('uuid2', 'Fred', 30);

select * from pykli_json where `firstName` = 'Tom';
select * from pykli_json where `Age` > 20;

exit;
""")

    runner = CliRunner()
    r = runner.invoke(main, [ksqldb.url])
    output = r.output.split("\n")

    assert r.exit_code == 0
    assert "Stream created" in output
    assert output.count("| ID    | firstName | Age |") == 2
    assert output.count("| uuid1 | Tom       |  20 |") == 1
    assert output.count("| uuid2 | Fred      |  30 |") == 1

    assert "pykli_json" in ksqldb.list_topic_names()
    assert "PYKLI_JSON" in ksqldb.list_stream_names()

    mock_input.send_text("""
drop stream pykli_json delete topic;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Source `PYKLI_JSON` (topic: pykli_json) was dropped." in r.output

    assert "pykli_json" not in ksqldb.list_topic_names()
    assert "PYKLI_JSON" not in ksqldb.list_stream_names()
