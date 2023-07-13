import httpx
from pprint import pformat

from . import LOG
from .tokens import Stmt, ErrMsg, StmtResponse, Info, PullQuery, QueryResponse, SessionVar


class pykli_eval:
    def __init__(self, ksqldb):
        self._ksqldb = ksqldb


    def __call__(self, token) -> StmtResponse | QueryResponse | ErrMsg | None:
        try:
            LOG.debug(f"pykli_eval: token={token}")
            match token:
                case Info(srv):
                    info = self._ksqldb.info()
                    return StmtResponse([info | {"@type": "info", "server": srv}])
                case Stmt(ksql):
                    resp = self._ksqldb.stmt(ksql)
                    LOG.debug(f"KSQL={ksql}, response={pformat(resp)}")
                    return StmtResponse(resp)
                case PullQuery(ksql):
                    resp = self._ksqldb.pull_query(ksql)
                    LOG.debug(f"KSQL={ksql}, response={pformat(resp)}")
                    return QueryResponse(resp)
                case ErrMsg():
                    return token
                case SessionVar(nm, val):
                    if val is not None:
                        self._ksqldb.define(nm, val)
                    else:
                        self._ksqldb.undefine(nm)
                    return None
                case _:
                    return ErrMsg(f"not yet implemented: {token}")
        except httpx.HTTPStatusError as e:
            return ErrMsg(e.response.json()["message"])
        except httpx.TransportError as e:
            return ErrMsg(f"Transport error: {pformat(e)}")
