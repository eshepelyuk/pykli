import httpx
import click
from pprint import pformat, pprint
from pygments.lexers.sql import SqlLexer
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import style_from_pygments_cls
from . import CONFIG_DIR, MONOKAI_STYLE
from .ksqldb import KsqlDBClient, is_stmt
from .printer import print_stmt
from .completer import pykli_completer
from .keybindgings import pykli_keys

def cli_loop(server):
    ksqldb = KsqlDBClient(server)

    session = PromptSession(
        lexer=PygmentsLexer(SqlLexer), style=style_from_pygments_cls(MONOKAI_STYLE),
        include_default_pygments_style=False,
        history=FileHistory(CONFIG_DIR / "history"), auto_suggest=AutoSuggestFromHistory(),
        completer=pykli_completer,
        multiline=True, key_bindings=pykli_keys(),
    )

    while True:
        try:
            text = session.prompt("pykli> ")
            if is_stmt(text):
                resp = ksqldb.stmt(text)
                print_stmt(resp)
            # elif text.startswith("describe"):
                # response = await client.ksql(text if text.endswith(";") else f"{text};")
                # json = response[0]
                # data = [(s["name"], s["schema"]["type"] if s["schema"]["fields"] is None else pformat(s["schema"]["fields"]))
                    # for s in json[f"{json['@type']}"]["fields"]]

                # click.secho("\n".join(format_output(data, ("Field", "Type"), format_name="psql")))
            elif text == "quit" or text == "exit":
                break
        except httpx.HTTPStatusError as e:
            click.secho(str(e), fg="red")
        except httpx.TransportError as e:
            click.secho(f"Transport error: {pformat(e)}", fg="red")
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

