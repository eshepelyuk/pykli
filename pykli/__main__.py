import click
import asyncio
from .cli import cli_loop
from . import CONFIG_DIR

@click.command()
@click.argument("server", default = "http://localhost:8088")
def main(server):
    """
    pykli - ksqlDB command line client written in Python.

    \b SERVER The address of the KsqlDB server."""

    CONFIG_DIR.mkdir(exist_ok=True, parents=True)
    cli_loop(server)

if __name__ == "__main__":
    main()
