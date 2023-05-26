import click
from ksqldb import KSQLdbClient
from prompt_toolkit import PromptSession
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.history import FileHistory
from pygments.lexers.sql import SqlLexer
from xdg_base_dirs import xdg_config_home
from . import CONFIG_DIR

async def cli_loop(server):
    client = KSQLdbClient(server)
    session = PromptSession(lexer=PygmentsLexer(SqlLexer),
        history=FileHistory(CONFIG_DIR / 'history'))

    while True:
        try:
            text = await session.prompt_async('pykli> ')
            json = await client.ksql_async(text)
            # json = client.ksql(text)
            click.echo(json)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    print('GoodBye!')

