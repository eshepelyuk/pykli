from prompt_toolkit.completion import NestedCompleter

pykli_completer = NestedCompleter.from_nested_dict({
    "describe": {
        "streams": None,
        "tables": None,
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
