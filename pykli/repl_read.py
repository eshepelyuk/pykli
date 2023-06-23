from pygments.lexers.sql import SqlLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit import PromptSession

from pathlib import Path
from sqlparse.tokens import DML, String, Keyword
import sqlparse

from . import MONOKAI_STYLE, HISTORY_FILE
from .completer import pykli_completer
from .keybindgings import pykli_keys
from .tokens import KStmt, ErrorMessage, KRunScript


class pykli_prompt:
    def __init__(self):
        self._session = PromptSession(
            lexer=PygmentsLexer(SqlLexer),
            style=style_from_pygments_cls(MONOKAI_STYLE), include_default_pygments_style=False,
            history=FileHistory(HISTORY_FILE), auto_suggest=AutoSuggestFromHistory(),
            completer=pykli_completer(),
            key_bindings=pykli_keys(),
            multiline=True, prompt_continuation=self._prompt_continuation,
            enable_open_in_editor=True,
        )

    def _prompt_continuation(self, width, line_number, is_soft_wrap): return " "

    def __call__(self):
        try:
            return self._session.prompt("pykli> ").strip()
        except KeyboardInterrupt:
            return ""
        except EOFError:
            return "exit"


def tokenize_sql_stmt(stmt):
    kw = stmt.token_first()
    if kw.ttype == Keyword and kw.ttype is not DML:
        yield KStmt(stmt.value)
    elif kw.ttype is KRunScript:
        yield from tokenize_script(stmt)
    else:
        yield stmt


def tokenize_script(stmt):
    _, path_token = stmt.token_next(0)
    if path_token.ttype is String.Single:
        path = Path(path_token.value.strip("'"))
        if path.exists():
            for stmt in sqlparse.parse(path.read_text()):
                yield from tokenize_sql_stmt(stmt)
        else:
            yield ErrorMessage(f"'{path}' not found")
    else:
        yield ErrorMessage(f"syntax error: {stmt}")


def pykli_read(prompt):
    has_next = True
    while has_next:
        for stmt in sqlparse.parse(prompt()):
            if stmt.value.startswith(("quit", "exit")):
                has_next = False
                break
            else:
                yield from tokenize_sql_stmt(stmt)

