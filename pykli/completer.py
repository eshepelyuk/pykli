from prompt_toolkit.completion import NestedCompleter

pykli_completer = NestedCompleter.from_nested_dict({
    "describe": {
        "connector": None,
        "function": None,
        "streams": None,
        "tables": None,
    },
    "drop": {
        "connector": {"if exists": None},
        "stream": {"if exists": None},
        "table": {"if exists": None},
        "type": {"if exists": None},
    },
    "list": {
        "connectors": None,
        "functions": None,
        "properties": None,
        "queries": None,
        "topics": None,
        "streams": None,
        "tables": None,
        "types": None,
        "variables": None,
    },
    "show": {
        "connectors": None,
        "functions": None,
        "properties": None,
        "queries": None,
        "topics": None,
        "streams": None,
        "tables": None,
        "types": None,
        "variables": None,
    },
    "exit": None,
})
