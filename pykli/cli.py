import httpx
from pprint import pformat
from pygments.lexers.sql import SqlLexer
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from . import HISTORY_FILE, MONOKAI_STYLE
from .ksqldb import KsqlDBClient, is_stmt
from .printer import print_stmt, pok, perr
from .completer import pykli_completer
from .keybindgings import pykli_keys


def cli_loop(server):
    ksqldb = KsqlDBClient(server)

    session = PromptSession(
        lexer=PygmentsLexer(SqlLexer), style=style_from_pygments_cls(MONOKAI_STYLE),
        include_default_pygments_style=False,
        history=FileHistory(HISTORY_FILE), auto_suggest=AutoSuggestFromHistory(),
        completer=pykli_completer,
        multiline=True, key_bindings=pykli_keys(),
    )

    while True:
        try:
            text = session.prompt("pykli> ")
            if is_stmt(text):
                resp = ksqldb.stmt(text)
                print_stmt(resp)
            elif text == "quit" or text == "exit":
                break
        except httpx.HTTPStatusError as e:
            perr(e.response.json()["message"])
        except httpx.TransportError as e:
            perr(f"Transport error: {pformat(e)}")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

