import click
import sqlparse
from pprint import pformat
from textwrap import wrap

from pygments.token import Token

from cli_helpers.tabular_output import format_output
from cli_helpers.tabular_output.preprocessors import style_output

from . import MONOKAI_STYLE

DESCRIBE_HEADERS = ("Field", "Type")

KSQL_SHOW_TYPES = {
    "connector_list": (
        lambda j : j["connectors"],
        ("Connector Name", "Type", "Class", "Status"),
        lambda rows : ((r["name"], r["type"], r["className"], r["state"]) for r in rows)
    ),
    "function_names": (
        lambda j : j["functions"],
        ("Function Name", "Category"),
        lambda rows : ((r["name"], r["category"]) for r in rows),
    ),
    "properties": (
        lambda j : sorted(j["properties"], lambda r: r["name"]),
        ("Name", "Scope", "Default override", "Effective Value"),
        lambda rows : ((r["name"], r["scope"], None, r["value"]) for r in rows),
    ),
    "queries": (
        lambda j : j["queries"],
        ("Query ID", "Query Type", "Status", "Sink Name", "Sink Kafka Topic", "Query String"),
        lambda rows : ((r["id"], r["queryType"], r["state"], r["sinks"], r["sinkKafkaTopics"],
                        sqlparse.format(r["queryString"], indent=True)) for r in rows),
    ),
    "kafka_topics": (
        lambda j : sorted(j["topics"], key=lambda r: r["name"]),
        ("Kafka Topic", "Partitions", "Partition Replicas"),
        lambda rows : ((r["name"], len(r["replicaInfo"]), r["replicaInfo"][0]) for r in rows)
    ),
    "streams": (
        lambda j : sorted(j["streams"], key=lambda r: r["name"]),
        ("Stream Name", "Kafka Topic", "Key Format", "Value Format", "Windowed"),
        lambda rows : ((r["name"], r["topic"], r["keyFormat"], r["valueFormat"], str(r["isWindowed"])) for r in rows)
    ),
    "tables": (
        lambda j : sorted(j["tables"], key=lambda r: r["name"]),
        ("Table Name", "Kafka Topic", "Key Format", "Value Format", "Windowed"),
        lambda rows : ((r["name"], r["topic"], r["keyFormat"], r["valueFormat"], str(r["isWindowed"])) for r in rows)
    ),
    "type_list": (
        lambda j : ({"name": nm, "schema": sc} for nm, sc in j["types"].items()),
        ("Name", "Schema"),
        lambda rows : ((r["name"], format_ksql_type(r)) for r in rows),
    ),
}

def pok(text):
    click.secho(text)


def pwarn(text):
    click.secho(text)


def perr(text):
    click.secho(text, fg="red")


def format_ksql_type(type_def) -> str:
    match type_def:
        case {"type": "KEY", "schema": {"type": "STRING"}}:
            return "VARCHAR (key)"
        case {"schema": {"type": "STRING"}}:
            return "VARCHAR"
        case {"schema": {"type": "STRUCT", "fields": flds}}:
            types_str = "\n".join(wrap(', '.join(f['name'] for f in flds), width=70))
            return f"STRUCT<{types_str}>"
        case {"type": "KEY", "schema": {"type": tp}}:
            return f"{tp} (key)"
        case {"type": "HEADER", "headerKey": hdr, "schema": {"type": tp}}:
            return f"{tp} (header('{hdr}'))"
        case {"schema": {"type": tp}}:
            return tp
        case _:
            return pformat(type_def)


def print_show(data_type, json):
    if data_type in KSQL_SHOW_TYPES:
        data_extractor, headers, row_extractor = KSQL_SHOW_TYPES[data_type]
        data = data_extractor(json)
        ff = format_output(row_extractor(data), headers, format_name="psql", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None,
            style=MONOKAI_STYLE, iinclude_default_pygments_style=False)

        pok("\n".join(ff))
    else:
        perr(f"`show` not implemented for: {data_type}")
        pok(pformat(json))


def print_describe(data):
    def row_extractor(rows): return ((r["name"], format_ksql_type(r)) for r in rows)
    ff = format_output(row_extractor(data), DESCRIBE_HEADERS, format_name="psql", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None,
            style=MONOKAI_STYLE, include_default_pygments_style=False)
    pok("\n".join(ff))


def print_stmt(resp):
    for json in resp:
        stmt = json["statementText"]
        if stmt.startswith("show"):
            print_show(json["@type"], json)
        elif stmt.startswith("describe"):
            print_describe(json["sourceDescription"]["fields"])
        elif stmt.startswith("drop"):
            match json:
                case {'@type': 'drop_connector'}:
                    click.secho(stmt)
                case {'@type': 'warning_entity', "message": msg}:
                    click.secho(msg)
                case {'@type': "currentStatus", "commandStatus": {"message": msg}}:
                    click.secho(msg)
                case _:
                    pok(pformat(json))
        else:
            perr(f"not implemented: {stmt}")

