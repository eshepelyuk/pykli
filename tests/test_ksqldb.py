import pytest
import httpx


@pytest.mark.e2e
def test_define_stmt(ksqldb):
    ksqldb.define("ff", "TO_JSON_STRING")
    r = ksqldb.stmt("describe function ${ff};")
    assert len(r) == 1
    assert r[0]["@type"] == "describe_function"

    ksqldb.undefine("ff")
    with pytest.raises(httpx.HTTPStatusError) as ex:
        ksqldb.stmt("describe function ${ff};")
    assert ex.value.response.json()["message"] == "Can't find any functions with the name '${ff}'"


@pytest.mark.e2e
def test_define_pull_query(ksqldb):
    ksqldb.define("ff", "KSQL_PROCESSING_LOG")
    r = ksqldb.pull_query("select * from ${ff};")
    assert len(r) == 1
    assert "columnNames" in r[0]

    ksqldb.undefine("ff")
    with pytest.raises(httpx.HTTPStatusError) as ex:
        ksqldb.pull_query("select * from ${ff};")
    assert ex.value.response.json()["statementText"] == "${FF}"

