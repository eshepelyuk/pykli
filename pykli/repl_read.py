from pygments.lexers.sql import SqlLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from prompt_toolkit import PromptSession
from prompt_toolkit.validation import Validator

from . import MONOKAI_STYLE, HISTORY_FILE
from .completer import pykli_completer
from .keybindgings import pykli_keys


def is_sql_valid(text):
    return True


input_validator = Validator.from_callable(
    is_sql_valid,
    error_message='This input is not valid ksqlDB syntax',
    move_cursor_to_end=True
)


def prompt_continuation(width, line_number, is_soft_wrap): return " "


def pykli_prompt():
    return PromptSession(
        lexer=PygmentsLexer(SqlLexer),
        style=style_from_pygments_cls(MONOKAI_STYLE), include_default_pygments_style=False,
        history=FileHistory(HISTORY_FILE), auto_suggest=AutoSuggestFromHistory(),
        completer=pykli_completer(),
        key_bindings=pykli_keys(),
        multiline=True, prompt_continuation=prompt_continuation, validator=input_validator,
        enable_open_in_editor=True,
    )

