import pytest
import sqlparse

from pykli.tokens import KSQL, KRunScript, initialize_sqlparse

@pytest.fixture(scope="module", autouse=True)
def ksqldb_mock():
    initialize_sqlparse()


@pytest.mark.parametrize("ksql", [
    ("  RUN   SCRIPT   '/qwe/asd/asd.ksql';"),
    ("run   SCRIPT   '/qwe/asd/asd.ksql'"),
])
def test_sqlparse_run_script(ksql):
    stmts = sqlparse.parse(ksql)
    assert len(stmts) == 1

    t = stmts[0].token_first()
    assert t.ttype == KRunScript


@pytest.mark.parametrize("ksql", [
    ("define qwe = 'asd;"),
    ("  define   qwe = 'asd "),
    ("DEFINE qwe = 'asd;"),
    ("  DEFINE   qwe = 'asd "),
])
def test_sqlparse_define(ksql):
    stmts = sqlparse.parse(ksql)
    assert len(stmts) == 1

    t = stmts[0].token_first()
    assert t.ttype == KSQL.Define


@pytest.mark.parametrize("ksql", [
    ("undefine qwe;"),
    ("  undefine   qwe "),
    ("  UNDEFINE  qwe "),
])
def test_sqlparse_undefine(ksql):
    stmts = sqlparse.parse(ksql)
    assert len(stmts) == 1

    t = stmts[0].token_first()
    assert t.ttype == KSQL.Undefine
