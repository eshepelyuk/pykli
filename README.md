# pyKLI

Interactive [ksqlDB](https://ksqldb.io/) command line client
with autocompletion and syntax highlighting written in Python.

This project is in an early preview stage. Please try it and provide your feedback.

PRs and suggestions are welcome.

## Installation

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
* `INSERT` for values

## TODO (prioritized)

* Session variables: `DEFINE`, `UNDEFINE`, `SHOW VARIABLES`
* `INSERT ... SELECT ... EMIT CHANGES`
* Semantic versioned release and publish to PyPI
* Auto detect when needed output via pager
* Push queries, i.e. with `EMIT CHANGES` for `SELECT` statement
* In-place KSQL editing with default editor
* Full KSQL syntax support with Pygments
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


