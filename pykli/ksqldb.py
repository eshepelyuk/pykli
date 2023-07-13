import base64
import httpx
from pprint import pformat

class KsqlDBClient:
    def __init__(self, url, api_key=None, api_secret=None):
        # TODO introduce common headers
        self._url = url
        self._headers = {"Content-Type": "application/vnd.ksql.v1+json"}
        self._client = httpx.Client(base_url=url, http2=True)
        self._session_vars = {}

        if api_key and api_secret:
            b64string = base64.b64encode(bytes(f"{api_key}:{api_secret}"))
            self._headers["Authorization"] = f"Basic {b64string}"


    @property
    def url(self):
        return self._url


    def define(self, name: str, value: str) -> None:
        self._session_vars[name] = value


    def undefine(self, name: str) -> None:
        del self._session_vars[name]


    def info(self):
        r = self._client.get("/info", headers=self._headers)
        r.raise_for_status()
        return r.json()["KsqlServerInfo"]


    def stmt(self, ksql_str):
        body = {"ksql": ksql_str, "sessionVariables": self._session_vars}
        r = self._client.post("/ksql", json=body, headers=self._headers)
        r.raise_for_status()
        return r.json()


    def pull_query(self, ksql_str):
        body = {"sql": ksql_str, "sessionVariables": self._session_vars}
        headers = {"Accept": "application/json"}
        r = self._client.post("/query-stream", json=body, headers=headers)
        r.raise_for_status()
        return r.json()


    # async def query_async(self, query_string, stream_properties=None, timeout=10):
    #     async for x in self.api.query(
    #         query_string=query_string,
    #         timeout=timeout,
    #         stream_properties=stream_properties,
    #     ):
    #         yield x

    # def close_query(self, query_id):
        # return self.api.close_query(query_id)

    # def inserts_stream(self, stream_name, rows):
        # return self.api.inserts_stream(stream_name, rows)
