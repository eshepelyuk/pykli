import httpx
import sys
import click
from pprint import pformat

from .ksqldb import KsqlDBClient, is_stmt
from .printer import print_stmt, perr, pok
from .repl_read import pykli_prompt


def repl(ksqldb: KsqlDBClient):
    session = pykli_prompt()

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

    return 0


@click.command()
@click.argument("server", default = "http://localhost:8088")
def main(server):
    """
    pyKLI - ksqlDB command line client.

    \b SERVER The address of the ksqlDB server."""

    ksqldb = KsqlDBClient(server)

    try:
        info = ksqldb.info()
        pok(f"Connected to {server}, version: {info['version']}, status: {info['serverStatus']}")
    except httpx.HTTPError as e:
        perr(f"Transport error: {pformat(e)}")
        sys.exit(1)

    sys.exit(repl(ksqldb))


if __name__ == "__main__":
    main()
