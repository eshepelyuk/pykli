import pytest
from click.testing import CliRunner

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from pykli.__main__ import main
from .conftest import list_type_names, list_topic_names, list_stream_names, list_connector_names

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

    assert "pykli_stream_json" in list_topic_names(ksqldb)
    assert "PYKLI_STREAM_JSON" in list_stream_names(ksqldb)

    mock_input.send_text("""
drop stream pykli_stream_json delete topic;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Source `PYKLI_STREAM_JSON` (topic: pykli_stream_json) was dropped." in r.output

    assert "pykli_stream_json" not in list_topic_names(ksqldb)
    assert "PYKLI_STREAM_JSON" not in list_stream_names(ksqldb)


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
    assert "PYKLI_TYPE" in list_type_names(ksqldb)

    mock_input.send_text("""
drop type if exists pykli_type;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Dropped type 'PYKLI_TYPE'" in r.output
    assert "PYKLI_TYPE" not in list_type_names(ksqldb)


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

    assert "PYKLI_CONNECTOR" in list_connector_names(ksqldb)
    assert "pykli_connector" in list_topic_names(ksqldb)

    mock_input.send_text("""
drop connector if exists pykli_connector;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])
    assert r.exit_code == 0
    assert "PYKLI_CONNECTOR" not in list_connector_names(ksqldb)


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

    assert "pykli_json" in list_topic_names(ksqldb)
    assert "PYKLI_JSON" in list_stream_names(ksqldb)

    mock_input.send_text("""
drop stream pykli_json delete topic;
exit;
""")

    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Source `PYKLI_JSON` (topic: pykli_json) was dropped." in r.output

    assert "pykli_json" not in list_topic_names(ksqldb)
    assert "PYKLI_JSON" not in list_tlist_stream_names(ksqldb)
