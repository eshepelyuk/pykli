import sqlparse
import pytest
from pykli.tokens import initialize_sqlparse, Stmt, SessionVar, KRunScript
from pykli.repl_read import tokenize_ksql


@pytest.fixture(scope="module", autouse=True)
def ksqldb_mock():
    initialize_sqlparse()

# TODO implement proper test
@pytest.mark.parametrize("ksql", [
    ("  RUN   SCRIPT   '/qwe/asd/asd.ksql';"),
    ("run   SCRIPT   '/qwe/asd/asd.ksql'"),
])
def test_tokenize_ksql_run_script(ksql):
    stmts = sqlparse.parse(ksql)
    assert len(stmts) == 1

    t = stmts[0].token_first()
    assert t.ttype == KRunScript


@pytest.mark.parametrize("ksql", [
    ("define my_var = 'my_val';"),
    ("  define   my_var  =  'my_val' "),
    ("DEFINE my_var = 'my_val';"),
    ("  DEFINE   my_var  =  'my_val' "),
])
def test_tokenize_ksql_define(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_ksql(stmt))
    assert isinstance(t, SessionVar)
    assert t.name == "my_var"
    assert t.val == "my_val"


@pytest.mark.parametrize("ksql", [
    ("undefine my_var;"),
    ("  undefine   my_var "),
    ("  UNDEFINE  my_var"),
])
def test_tokenize_ksql_undefine(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_ksql(stmt))
    assert isinstance(t, SessionVar)
    assert t.name == "my_var"
    assert t.val is None


# TODO more test
@pytest.mark.parametrize("ksql", [
    ("show variables;"),
    ("  SHOW variables "),
])
def test_tokenize_ksql_stmt(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_ksql(stmt))
    assert isinstance(t, Stmt)
