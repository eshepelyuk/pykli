import click
import sqlparse
from pprint import pformat, pprint

from pygments.token import Token

from cli_helpers.tabular_output import format_output
from cli_helpers.tabular_output.preprocessors import style_output

from . import MONOKAI_STYLE

KSQL_SHOW_TYPES = {
    "connector_list": (
        lambda j : j["connectors"],
        ("Connector Name", "Type", "Class", "Status"),
        lambda row : ((s["name"], s["type"], s["className"], s["state"]) for s in row)
    ),
    "function_names": (
        lambda j : j["functions"],
        ("Function Name", "Category"),
        lambda row : ((s["name"], s["category"]) for s in row),
    ),
    "properties": (
        lambda j : j["properties"],
        ("Name", "Scope", "Default override", "Effective Value"),
        lambda row : ((s["name"], s["scope"], None, s["value"]) for s in row),
    ),
    "queries": (
        lambda j : j["queries"],
        ("Query ID", "Query Type", "Status", "Sink Name", "Sink Kafka Topic", "Query String"),
        lambda row : ((s["id"], s["queryType"], s["state"], s["sinks"], s["sinkKafkaTopics"],
                        sqlparse.format(s["queryString"], indent=True)) for s in row),
    ),
    "kafka_topics": (
        lambda j : j["topics"],
        ("Kafka Topic", "Partitions", "Partition Replicas"),
        lambda row : ((s["name"], len(s["replicaInfo"]), s["replicaInfo"][0]) for s in row)
    ),
    "streams": (
        lambda j : j["streams"],
        ("Stream Name", "Kafka Topic", "Key Format", "Value Format", "Windowed"),
        lambda row : ((s["name"], s["topic"], s["keyFormat"], s["valueFormat"], str(s["isWindowed"])) for s in row)
    ),
    "tables": (
        lambda j : j["tables"],
        ("Table Name", "Kafka Topic", "Key Format", "Value Format", "Windowed"),
        lambda row : ((s["name"], s["topic"], s["keyFormat"], s["valueFormat"], str(s["isWindowed"])) for s in row)
    ),
    "type_list": (
        lambda j : j["types"].items(),
        ("Name", "Schema"),
        lambda row : ((s[0], pformat(s[1])) for s in row),
    ),
}

def print_show(data_type, json):
    if data_type in KSQL_SHOW_TYPES:
        data_extractor, headers, row_extractor = KSQL_SHOW_TYPES[data_type]
        data = data_extractor(json)
        ff = format_output(row_extractor(data), headers, format_name="psql", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None,
            style=MONOKAI_STYLE, include_default_pygments_style=False)

        click.secho("\n".join(ff))
        # click.echo_via_pager("\n".join(ff))
    else:
        click.secho(f"`show` not implemented for: {data_type}", fg="red")
        pprint(json)

def print_describe(json):
    click.secho(f"`describe` not implemented", fg="red")
    pprint(json)

def print_stmt(resp):
    for json in resp:
        stmt = json["statementText"]
        if stmt.startswith("show"):
            print_show(json["@type"], json)
        elif stmt.startswith("describe"):
            print_describe(json)
        else:
            click.secho(f"not implemented: {stmt}", fg="red")

