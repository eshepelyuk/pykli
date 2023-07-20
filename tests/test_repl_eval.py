import pytest
import sqlparse
from pykli.repl_eval import pykli_eval
from pykli.tokens import Info, SessionVar, Stmt, StmtResponse


@pytest.fixture
def ksqldb_mock(mocker):
    return mocker.patch("pykli.ksqldb.KsqlDBClient", autospec=True)


def test_eval_info(ksqldb_mock):
    ksqldb_mock.info.return_value = {"ksql": "info"}

    req = Info("mys_srv")
    resp = pykli_eval(ksqldb_mock)(req)
    ksqldb_mock.info.assert_called_once()
    assert isinstance(resp, StmtResponse)
    assert resp.val[0] == {"@type": "info", "server": req.srv, "ksql": "info"}


def test_eval_define(ksqldb_mock):
    e = pykli_eval(ksqldb_mock)

    resp = e(SessionVar("var1", "some_value"))
    assert resp is None
    ksqldb_mock.define.assert_called_once_with("var1", "some_value")

    resp = e(SessionVar("var1", None))
    assert resp is None
    ksqldb_mock.undefine.assert_called_once_with("var1")


def test_eval_show_vars(mocker, ksqldb_mock):
    p = mocker.PropertyMock(return_value={"p1":"v1"})
    type(ksqldb_mock).session_vars = p

    stmt = sqlparse.parse("show variables;")[0]
    resp = pykli_eval(ksqldb_mock)(Stmt(stmt))
    assert isinstance(resp, StmtResponse)
    assert len(resp.val) == 1
    assert resp.val[0]["@type"] == "show_variables"
    ksqldb_mock.stmt.assert_not_called()
    p.assert_called_once()
