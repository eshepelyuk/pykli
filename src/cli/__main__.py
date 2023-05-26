import click
import asyncio
from xdg_base_dirs import xdg_config_home
from .cli import cli_loop
from . import CONFIG_DIR

@click.command()
@click.argument("server", default = "http://localhost:8088")
def main(server):
    """
    pykli is Python client for KsqlDB.

    \b SERVER The address of the KsqlDB server."""

    CONFIG_DIR.mkdir(exist_ok=True, parents=True)
    asyncio.run(cli_loop(server))

if __name__ == "__main__":
    main()
