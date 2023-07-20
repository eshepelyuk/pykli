import pytest
from click.testing import CliRunner

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from pykli.__main__ import main
from .conftest import list_type_names, list_topic_names, list_stream_names, list_connector_names, list_table_names, list_query_ids


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
define ff = 'TO_JSON_STRING';
show functions;
describe function ${ff};
show variables;
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
    assert "| Variable Name | Value          |" in r.output
    assert "| ff            | TO_JSON_STRING |" in r.output


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


@pytest.mark.e2e
def test_tables(mock_input, ksqldb):
    mock_input.send_text("""
create or replace table pykli_table_json (
    id varchar primary key, `firstName` varchar, "Age" int
) with (kafka_topic = 'pykli_table_json', partitions = 1, value_format = 'json');
describe pykli_table_json;
show tables;
show topics;

create table query_pykli_table_json as select * from pykli_table_json;
show queries;

exit;
""")

    runner = CliRunner()
    r = runner.invoke(main, [ksqldb.url])
    output = r.output.split("\n")

    assert r.exit_code == 0
    assert "Table created" in output
    assert "| Field     | Type          |" in output
    assert "| ID        | VARCHAR (key) |" in output
    assert "| Table Name       | Kafka Topic      | Key Format | Value Format | Windowed |" in output
    assert "| PYKLI_TABLE_JSON | pykli_table_json | KAFKA      | JSON         | False    |" in output

    queries = list_query_ids(ksqldb)
    assert len(queries) == 1

    assert f"Created query with ID {queries[0]}" in output
    assert "| Query ID" in r.output
    assert f"| {queries[0]} | PERSISTENT | RUNNING |" in r.output

    assert "pykli_table_json" in list_topic_names(ksqldb)
    assert "PYKLI_TABLE_JSON" in list_table_names(ksqldb)

    mock_input.send_text(f"""
terminate {queries[0]};
exit;
""")
    r = runner.invoke(main, [ksqldb.url])

    assert "Query terminated." in r.output
    assert len(list_query_ids(ksqldb)) == 0

    mock_input.send_text("""
drop table query_pykli_table_json delete topic;
drop table pykli_table_json delete topic;
exit;
""")
    r = runner.invoke(main, [ksqldb.url])

    assert r.exit_code == 0
    assert "Source `QUERY_PYKLI_TABLE_JSON` (topic: QUERY_PYKLI_TABLE_JSON) was dropped." in r.output
    assert "Source `PYKLI_TABLE_JSON` (topic: pykli_table_json) was dropped." in r.output

    assert "pykli_table_json" not in list_topic_names(ksqldb)
    assert "PYKLI_TABLE_JSON" not in list_table_names(ksqldb)
