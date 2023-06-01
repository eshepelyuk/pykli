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
    def row_extractor(rows):
        for r in rows:
            yield (r["name"], format_ksql_type(r))
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

