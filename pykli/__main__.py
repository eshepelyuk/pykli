import httpx
import sys
import click
from pprint import pformat
from .printer import pok, perr
from .ksqldb import KsqlDBClient
from .cli import cli_loop
from . import CONFIG_DIR

@click.command()
@click.argument("server", default = "http://localhost:8088")
def main(server):
    """
    pykli - ksqlDB command line client written in Python.

    \b SERVER The address of the ksqlDB server."""

    CONFIG_DIR.mkdir(exist_ok=True, parents=True)

    ksqldb = KsqlDBClient(server)

    try:
        info = ksqldb.info()
        pok(f"Connected to {server}, version: {info['version']}, status: {info['serverStatus']}")
    except httpx.HTTPError as e:
        perr(f"Transport error: {pformat(e)}")
        sys.exit(1)

    sys.exit(cli_loop(ksqldb))

if __name__ == "__main__":
    main()
