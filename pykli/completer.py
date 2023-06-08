from prompt_toolkit.completion import NestedCompleter, Completer #, Completion, CompleteEvent
from prompt_toolkit.completion.word_completer import WordCompleter
from prompt_toolkit.document import Document
# from prompt_toolkit.application import get_app, run_in_terminal
# from typing import Any, Iterable, Mapping, Set, Union

COMPLETIONS = {
    "describe": {
        "connector": WordCompleter(["conn1", "conn2"]),
        "function": None,
        "streams": None,
        "tables": None,
    },
    "drop": {
        "connector": WordCompleter(["conn1", "conn2"]),
        "connector if exists": WordCompleter(["conn1", "conn2"]),
        "stream": {"if exists": None},
        "table": {"if exists": None},
        "type": {"if exists": None},
    },
    "list": {"connectors", "functions", "properties", "queries", "topics", "streams", "tables", "types", "variables"},
    "show": {"connectors", "functions", "properties", "queries", "topics", "streams", "tables", "types", "variables"},
    "exit": None,
    "quit": None,
}

class PykliCompleter(Completer):
    def __init__(self):
        self._nested = NestedCompleter.from_nested_dict(COMPLETIONS)

    def get_completions(self, document, complete_event):
        if document.on_first_line:
            yield from self._nested.get_completions(document, complete_event)
        else:
            text = document.current_line_before_cursor.lstrip()
            # stripped_len = len(document.current_line_before_cursor) - len(text)

            first_term = [ln for ln in document.lines if ln][0]
            completer = self._nested.options.get(first_term)

            if completer is not None:
                new_document = Document(
                    text,
                    cursor_position=len(text),
                )
                yield from completer.get_completions(new_document, complete_event)

            yield from ()


def pykli_completer(): return PykliCompleter()
