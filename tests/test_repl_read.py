import sqlparse
import pytest

from pykli.tokens import initialize_sqlparse, SessionVar
from pykli.repl_read import tokenize_sql_stmt


@pytest.fixture(scope="module", autouse=True)
def ksqldb_mock():
    initialize_sqlparse()


@pytest.mark.parametrize("ksql", [
    ("define my_var = 'my_val';"),
    ("  define   my_var  =  'my_val';"),
])
def test_tokenize_sql_stmt_define(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_sql_stmt(stmt))
    assert isinstance(t, SessionVar)
    assert t.name == "my_var"
    assert t.val == "my_val"


@pytest.mark.parametrize("ksql", [
    ("undefine my_var;"),
    ("  undefine   my_var ; "),
])
def test_tokenize_sql_stmt_undefine(ksql):
    stmt = sqlparse.parse(ksql)[0]
    t = next(tokenize_sql_stmt(stmt))
    assert isinstance(t, SessionVar)
    assert t.name == "my_var"
    assert t.val is None

