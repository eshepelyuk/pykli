import sys
import click
from . import LOG
from .ksqldb import KsqlDBClient
from .repl_read import pykli_prompt, pykli_read
from .repl_eval import pykli_eval
from .repl_print import pykli_print
from .tokens import Info, ErrorMessage, initialize_sqlparse


@click.command()
@click.argument("server", default = "http://localhost:8088")
def main(server):
    """
    pyKLI - ksqlDB command line client.

    \b SERVER The address of the ksqlDB server."""

    LOG.info(f"pyKLI started: server={server}")

    initialize_sqlparse()

    eval = pykli_eval(KsqlDBClient(server))

    if isinstance(pykli_print(eval(Info(server))), ErrorMessage):
        sys.exit(1)

    for token in pykli_read(pykli_prompt()):
        pykli_print(eval(token))

    sys.exit(0)


if __name__ == "__main__":
    main()
