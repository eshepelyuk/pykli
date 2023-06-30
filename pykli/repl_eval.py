from . import LOG
from .tokens import Stmt, ErrorMessage, KResponse, Info, PullQuery, QueryResponse

import httpx
from pprint import pformat

class pykli_eval:
    def __init__(self, ksqldb):
        self._ksqldb = ksqldb

    def __call__(self, token):
        try:
            LOG.debug(f"pykli_eval: token={token}")
            match token:
                case Info(srv):
                    info = self._ksqldb.info()
                    return KResponse([info | {"@type": "info", "server": srv}])
                case Stmt(ksql):
                    resp = self._ksqldb.stmt(ksql)
                    LOG.debug(f"KSQL={ksql}, response={pformat(resp)}")
                    return KResponse(resp)
                case PullQuery(ksql):
                    resp = self._ksqldb.pull_query(ksql)
                    LOG.debug(f"KSQL={ksql}, response={pformat(resp)}")
                    return QueryResponse(resp)
                case ErrorMessage():
                    return token
                case _:
                    return ErrorMessage(f"not yet implemented: {token}")
        except httpx.HTTPStatusError as e:
            return ErrorMessage(e.response.json()["message"])
        except httpx.TransportError as e:
            return ErrorMessage(f"Transport error: {pformat(e)}")
