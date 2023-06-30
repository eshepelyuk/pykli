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

## TODO

* Metadata autocompletion
    * table ans stream names
    * column names and functions in queries
    * topic and connector names
* Full KSQL syntax support with Pygments
* Configuration file
* Push queries, i.e. with `EMIT CHANGES`
* In-place KSQL editing with default editor
* Internal help
* Publish to PyPI
* Semantic versioning 
* Output via pager
