import httpx
import sys
import click
from pprint import pformat

from . import LOG
from .ksqldb import KsqlDBClient
from .repl_print import print_stmt, perr, pok
from .repl_read import pykli_prompt

def is_stmt(s): return (
    s.startswith(("show", "SHOW", "list", "LIST", "describe", "DESCRIBE")) or
    s.startswith(("drop", "DROP","create", "CREATE"))
)


def repl(ksqldb: KsqlDBClient):
    session = pykli_prompt()

    while True:
        try:
            text = session.prompt("pykli> ")
            if is_stmt(text):
                resp = ksqldb.stmt(text)
                LOG.debug(f"SQL={text}, ksqlDB={pformat(resp)}")
                print_stmt(resp)
            elif text == "quit" or text == "exit":
                break
        except httpx.HTTPStatusError as e:
            perr(e.response.json()["message"], e)
        except httpx.TransportError as e:
            perr(f"Transport error: {pformat(e)}", e)
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    return 0


@click.command()
@click.argument("server", default = "http://localhost:8088")
def main(server):
    """
    pyKLI - ksqlDB command line client.

    \b SERVER The address of the ksqlDB server."""

    LOG.info(f"pyKLI started: server={server}")

    ksqldb = KsqlDBClient(server)

    try:
        info = ksqldb.info()
        pok(f"Connected to {server}, version: {info['version']}, status: {info['serverStatus']}")
    except httpx.HTTPError as e:
        perr("Transport error", e)
        sys.exit(1)

    sys.exit(repl(ksqldb))


if __name__ == "__main__":
    main()
