import sys
import click
import pathlib

from . import LOG
from .ksqldb import KsqlDBClient
from .repl_read import pykli_prompt, pykli_read, file_prompt
from .repl_eval import pykli_eval
from .repl_print import pykli_print
from .tokens import Info, ErrMsg, initialize_sqlparse


@click.command()
@click.option('-f', '--file', help="execute commands from file, then exit",
    type=click.Path(exists=True, path_type=pathlib.Path))
@click.argument("server", default = "http://localhost:8088")
def main(server, file):
    """
    pyKLI - ksqlDB command line client.

    \b SERVER The address of the ksqlDB server."""

    LOG.info(f"pyKLI started: server={server}, file={file}")

    initialize_sqlparse()

    eval = pykli_eval(KsqlDBClient(server))
    prompt = pykli_prompt() if file is None else file_prompt(file)

    if isinstance(pykli_print(eval(Info(server))), ErrMsg):
        sys.exit(1)

    for token in pykli_read(prompt):
        pykli_print(eval(token))

    sys.exit(0)


if __name__ == "__main__":
    main()
