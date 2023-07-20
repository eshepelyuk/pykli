from pygments.lexers.sql import SqlLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit import PromptSession

from pprint import pformat
from pathlib import Path
from sqlparse.tokens import DML, DDL, String, Keyword
from sqlparse.sql import Comparison, Identifier
import sqlparse

from . import MONOKAI_STYLE, HISTORY_FILE, LOG
from .completer import pykli_completer
from .keybindgings import pykli_keys
from .tokens import KSQL, Stmt, ErrMsg, PullQuery, SessionVar
from .repl_print import pok

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


def tokenize_run_script(stmt):
    t = stmt.token_first()
    _, path_token = stmt.token_next(stmt.token_index(t))

    if path_token.ttype is String.Single:
        path = Path(path_token.value.strip("'"))
        if path.exists():
            for stmt in sqlparse.parse(path.read_text()):
                yield from tokenize_ksql(stmt)
        else:
            yield ErrMsg(f"file not found: {path}")
    else:
        yield ErrMsg(f"syntax error: {stmt}")


def tokenize_ksql(stmt):
    kw = stmt.token_first()

    LOG.debug(f"tokenize_ksql: stmt=<{stmt}>, first_token={pformat(kw)}")
    if kw.ttype == Keyword or kw.ttype == DDL or kw.match(DML, "insert"):
        yield Stmt(stmt)
    elif kw.match(DML, "select") and "emit changes" not in stmt.value.lower():
        yield PullQuery(stmt.value)
    elif kw.ttype is KSQL.RunScript:
        yield from tokenize_run_script(stmt)
    elif kw.ttype is KSQL.Define:
        _, cmp = stmt.token_next(stmt.token_index(kw))
        if isinstance(cmp, Comparison) and cmp.right.ttype is String.Single:
            yield SessionVar(cmp.left.value, cmp.right.value.strip("'"))
    elif kw.ttype is KSQL.Undefine:
        _, id = stmt.token_next(stmt.token_index(kw))
        if isinstance(id, Identifier):
            yield SessionVar(id.value, None)
    else:
        yield stmt


def pykli_read(prompt):
    while True:
        for stmt in sqlparse.parse(prompt()):
            if stmt.value.startswith(("quit", "exit")):
                return
            else:
                yield from tokenize_ksql(stmt)

