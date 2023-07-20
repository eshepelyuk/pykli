import sqlparse
import pytest
from pykli.tokens import initialize_sqlparse, Stmt, SessionVar, ErrMsg
from pykli.repl_read import tokenize_ksql


@pytest.fixture(scope="module", autouse=True)
def ksqldb_mock():
    initialize_sqlparse()

@pytest.mark.parametrize("ksql", [
    ('  RUN   SCRIPT   "/asd.ksql";'),
    ('  RUN   SCRIPT   `/asd.ksql`; '),
    ('  run   SCRIPT   "/asd.ksql"'),
    ('  run   SCRIPT   "/asd.ksql"  '),
])
def test_tokenize_ksql_run_script_syntax_err(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_ksql(stmt))
    assert isinstance(t, ErrMsg)
    assert t.msg == f"syntax error: {ksql}"


@pytest.mark.parametrize("ksql", [
    ("  RUN   SCRIPT   '/asd.ksql';"),
    ("run   SCRIPT   '/asd.ksql'"),
])
def test_tokenize_ksql_run_script_not_found(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_ksql(stmt))
    assert isinstance(t, ErrMsg)
    assert t.msg.startswith("file not found: /asd.ksql")


def test_tokenize_ksql_run_script(tmp_path):
    f = tmp_path / "file.ksql"
    f.write_text("show queries;\ndefine vvv = 'val';")

    stmt = sqlparse.parse(f"run script '{f}';")[0]
    tokens = list(tokenize_ksql(stmt))
    assert len(tokens) == 2
    assert isinstance(tokens[0], Stmt)
    assert tokens[0].ksql.value == "show queries;"
    assert isinstance(tokens[1], SessionVar)
    assert tokens[1].name == "vvv"
    assert tokens[1].val == "val"


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


@pytest.mark.parametrize("ksql", [
    ("insert into some_table select * from some_stream emit changes;"),
    ("insert into some_table select * from some_stream;"),
])
def test_tokenize_ksql_insert_select_emit_changes(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_ksql(stmt))
    assert isinstance(t, Stmt)
