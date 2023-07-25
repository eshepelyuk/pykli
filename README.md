# pyKLI

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
![PyPI - Version](https://img.shields.io/pypi/v/pykli?color=greenlight)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pykli)
![PyPI - License](https://img.shields.io/pypi/l/pykli)

Interactive [ksqlDB](https://ksqldb.io/) command line client
with autocompletion and syntax highlighting written in Python.

This project is in an early preview stage. Please try it and provide your feedback.

PRs and suggestions are welcome.

## Installation

* Latest released version
```sh
pip install pykli
```

* From latest source code
```sh
pip install -U git+https://github.com/eshepelyuk/pykli@main
```

## Supported KSQL commands

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

* Auto detect when needed output via pager
* Push queries, i.e. with `EMIT CHANGES` for `SELECT` statement
* In-place KSQL editing with default editor
* KSQL syntax support with Pygments
* Metadata autocompletion
    * table ans stream names
    * column names and functions in queries
    * topic and connector names
    * session variables
    * attributes of `WITH` blocks
* More configuration options and configuration file
    * pygments theme
    * server profiles
    * etc etc
* Internal help
* `PAUSE` / `RESUME`
* `DESCRIBE ... EXTENDED`
* `EXPLAIN`
