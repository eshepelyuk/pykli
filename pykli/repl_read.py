from pygments.lexers.sql import SqlLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit import PromptSession

from pprint import pformat
from pathlib import Path
from sqlparse.tokens import DML, DDL, String, Keyword
import sqlparse

from . import MONOKAI_STYLE, HISTORY_FILE, LOG
from .completer import pykli_completer
from .keybindgings import pykli_keys
from .tokens import Stmt, ErrMsg, KRunScript, PullQuery


class file_prompt:
    def __init__(self, path):
        self._path = path

    def __call__(self):
        if  self._path:
            ksql = self._path.read_text()
            self._path = None
            return ksql

        return "exit"


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


def tokenize_script(stmt):
    _, path_token = stmt.token_next(0)
    if path_token.ttype is String.Single:
        path = Path(path_token.value.strip("'"))
        if path.exists():
            for stmt in sqlparse.parse(path.read_text()):
                yield from tokenize_sql_stmt(stmt)
        else:
            yield ErrMsg(f"'{path}' not found")
    else:
        yield ErrMsg(f"syntax error: {stmt}")


def tokenize_sql_stmt(stmt):
    kw = stmt.token_first()

    # stmt._pprint_tree()

    LOG.debug(f"tokenize_sql_stmt: stmt=<{stmt}>, first_token={pformat(kw)}")
    if kw.ttype == Keyword or kw.ttype == DDL:
        yield Stmt(stmt.value)
    elif kw.match(DML, "insert"):
        yield Stmt(stmt.value)
    elif kw.match(DML, "select") and "emit changes" not in stmt.value.lower():
        yield PullQuery(stmt.value)
    elif kw.ttype is KRunScript:
        yield from tokenize_script(stmt)
    else:
        yield stmt


def pykli_read(prompt):
    has_next = True
    while has_next:
        for stmt in sqlparse.parse(prompt()):
            if stmt.value.startswith(("quit", "exit")):
                has_next = False
                break
            else:
                yield from tokenize_sql_stmt(stmt)

