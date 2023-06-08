import click
import sqlparse
from pprint import pformat
from textwrap import wrap

from pygments.token import Token

from cli_helpers.tabular_output import format_output
from cli_helpers.tabular_output.preprocessors import style_output

from . import MONOKAI_STYLE, LOG

DESCRIBE_SRC_HEADERS = ("Field", "Type")

DESCRIBE_FUNC_HEADERS = ("Name", "Author", "Version", "Description", "Type", "Jar")

DESCRIBE_FUNC_VARS_HEADERS = ("Signature", "Returns", "Description")

DESCRIBE_CONN_HEADERS = ("Name", "Class", "Type", "State", "WorkerId")

DESCRIBE_CONN_TASKS_HEADERS = {"Task ID", "State", "Error Trace"}

KSQL_SHOW_TYPES = {
    "connector_list": (
        lambda j : j["connectors"],
        ("Connector Name", "Type", "Class", "Status"),
        lambda rows : ((r["name"], r["type"], r["className"], r["state"]) for r in rows)
    ),
    "function_names": (
        lambda j : sorted(j["functions"], key=lambda r: (r["category"], r["name"])),
        ("Function Name", "Category"),
        lambda rows : ((r["name"], r["category"]) for r in rows),
    ),
    "properties": (
        lambda j : sorted(j["properties"], key=lambda r: r["name"]),
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


def pwarn(text, data=None):
    click.secho(text)
    LOG.warning(f"{text}, data={pformat(data)}")


def perr(text, data=None):
    click.secho(text, fg="red")
    LOG.error(f"{text}, data={pformat(data)}")


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
        pwarn(f"`show` not implemented for: {data_type}", json)


def print_describe_src(data):
    def row_extractor(rows): return ((r["name"], format_ksql_type(r)) for r in rows)
    ff = format_output(row_extractor(data["fields"]), DESCRIBE_SRC_HEADERS, format_name="psql", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None,
            style=MONOKAI_STYLE, include_default_pygments_style=False)
    pok("\n".join(ff))


def print_describe_conn(data):
    data_rows = [(data["status"]["name"], data["connectorClass"], data["status"]["type"],
        data["status"]["connector"]["state"], data["status"]["connector"]["worker_id"])]
    f1 = format_output(data_rows, DESCRIBE_CONN_HEADERS, format_name="vertical", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None, sep_title="Overview",
            style=MONOKAI_STYLE, include_default_pygments_style=False)
    pok("\n".join(f1))

    def task_extractor(rows): return ((r["id"], r["state"], r.get("trace", "")) for r in rows)
    f2 = format_output(task_extractor(data["status"]["tasks"]), DESCRIBE_CONN_TASKS_HEADERS,
            format_name="psql", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None,
            style=MONOKAI_STYLE, include_default_pygments_style=False)
    pok("\n".join(f2))


def print_func_variations(func_name, func_arr):
    def func_extractor(rows):
        for r in rows:
            args = [f"{a['name']} {a['type']}" for a in r["arguments"]]
            yield (f"{func_name}({', '.join(args)})", r["returnType"], r["description"])
    ff = format_output(func_extractor(func_arr), DESCRIBE_FUNC_VARS_HEADERS, format_name="psql", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None, sep_title="Variation #{n}",
            style=MONOKAI_STYLE, include_default_pygments_style=False)
    pok("\n".join(ff))


def print_describe_func(data):
    data_rows = [(data["name"], data["author"], data["version"], data["description"], data["type"], data["path"])]
    ff = format_output(data_rows, DESCRIBE_FUNC_HEADERS, format_name="vertical", preprocessors=(style_output,),
            header_token=Token.String, odd_row_token=None, even_row_token=None, sep_title="Overview",
            style=MONOKAI_STYLE, include_default_pygments_style=False)
    pok("\n".join(ff))
    print_func_variations(data["name"], data["functions"])


def print_stmt(json_arr):
    for json in json_arr:
        stmt = json["statementText"]
        if stmt.startswith(("show", "list", "SHOW", "LIST")):
            print_show(json["@type"], json)
        elif stmt.startswith("describe"):
            match json:
                case {"@type": "sourceDescription", "sourceDescription": data}:
                    print_describe_src(data)
                case {"@type": "source_descriptions", "sourceDescriptions": data_arr}:
                    for data in data_arr:
                        print_describe_src(data)
                case {"@type": "connector_description"}:
                    print_describe_conn(json)
                case {"@type": "describe_function"}:
                    print_describe_func(json)
                case _:
                    pwarn(f"unknown format {stmt}", json)
        elif stmt.startswith(("drop", "DROP")):
            match json:
                case {"@type": "drop_connector"}:
                    click.secho(stmt)
                case {"@type": "warning_entity", "message": msg}:
                    click.secho(msg)
                case {"@type": "currentStatus", "commandStatus": {"message": msg}}:
                    click.secho(msg)
                case _:
                    pwarn(f"unknown format {stmt}", json)
        else:
            perr(f"output not yet implemented: {stmt}", json)

