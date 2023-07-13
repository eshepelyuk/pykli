import pytest
from pykli.repl_eval import pykli_eval
from pykli.tokens import Info, SessionVar, StmtResponse


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
