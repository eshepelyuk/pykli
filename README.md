# pyKLI

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
![PyPI - Version](https://img.shields.io/pypi/v/pykli?color=greenlight)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pykli)
![PyPI - License](https://img.shields.io/pypi/l/pykli)

Interactive command line client for [ksqlDB](https://ksqldb.io/)
with autocompletion and syntax highlighting written in Python.

Inspired by and also borrowed some code from the great family of CLI tools https://www.dbcli.com/.

The project is in early stage, but usable for supported functionality.

All your PRs and suggestions are welcome.

## Installation

* Latest released version
```sh
pip install pykli
```

* From latest source code
```sh
pip install -U git+https://github.com/eshepelyuk/pykli@main
```
## Features

* Command history and search, history based autosuggestion.
* KSQL command keywords autocompletion.
* Run multiple commands from local file.
* Partial KSQL syntax highlighting based on `Pygments` SQL.
* Pretty tabular output with highlighting based on `Pygments` themes.
* Supported KSQL commands.

    * `SHOW`, `LIST`
    * `DESCRIBE`, without `EXTENDED`
    * `DROP`
    * `CREATE`
    * `RUN SCRIPT`
    * `TERMINATE`
    * `SELECT`  for Pull queries
    * `INSERT`
    * `DEFINE`, `UNDEFINE`

## TODO (prioritized)

* Push queries, i.e. with `EMIT CHANGES` for `SELECT` statement
* `PAUSE` / `RESUME`
* KSQL syntax support with Pygments
* `DESCRIBE ... EXTENDED`
* `EXPLAIN`
* Auto detect when needed output via pager
* Metadata autocompletion
    * table ans stream names
    * column names and functions in queries
    * topic and connector names
    * session variables
    * attributes of `WITH` blocks
* In-place KSQL editing with default editor
* Internal help
* More configuration options and configuration file
    * pygments theme
    * server profiles
    * etc etc
