from . import LOG
from .tokens import KStmt, ErrorMessage, KResponse, KInfo

import httpx
from pprint import pformat

class pykli_eval:
    def __init__(self, ksqldb):
        self._ksqldb = ksqldb

    def __call__(self, token):
        try:
            match token:
                case KInfo(srv):
                    info = self._ksqldb.info()
                    return KResponse([info | {"@type": "info", "server": srv}])
                case KStmt(val):
                    resp = self._ksqldb.stmt(val)
                    LOG.debug(f"KSQL={val}, response={pformat(resp)}")
                    return KResponse(resp)
                case ErrorMessage():
                    return token
                case _:
                    return ErrorMessage(f"not yet implemented: {token}")
        except httpx.HTTPStatusError as e:
            return ErrorMessage(e.response.json()["message"])
        except httpx.TransportError as e:
            return ErrorMessage(f"Transport error: {pformat(e)}")
