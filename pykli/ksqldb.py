import base64
import httpx


class KsqlDBClient:
    def __init__(self, url, api_key=None, api_secret=None):
        # TODO introduce common headers
        self._url = url
        self._headers = {"Content-Type": "application/vnd.ksql.v1+json"}
        self._client = httpx.Client(base_url=url, http2=True)

        if api_key and api_secret:
            b64string = base64.b64encode(bytes(f"{api_key}:{api_secret}"))
            self._headers["Authorization"] = f"Basic {b64string}"


    @property
    def url(self):
        return self._url


    def info(self):
        r = self._client.get("/info", headers=self._headers)
        r.raise_for_status()
        return r.json()["KsqlServerInfo"]


    def stmt(self, ksql_str, stream_props={}):
        body = {
            "ksql": ksql_str,
            "streamsProperties": stream_props,
            "sessionVariables": {},
        }
        r = self._client.post("/ksql", json=body, headers=self._headers)
        r.raise_for_status()
        return r.json()

    def pull_query(self, ksql_str, stream_props={}):
        body = {
            "sql": ksql_str,
            "streamsProperties": stream_props,
            "sessionVariables": {},
        }
        headers = {"Accept": "application/json"}
        r = self._client.post("/query-stream", json=body, headers=headers)
        r.raise_for_status()
        return r.json()


    def list_topic_names(self) -> list[str]:
        json = self.stmt("show topics;")[0]
        return [t["name"] for t in json["topics"]]


    def list_stream_names(self) -> list[str]:
        json = self.stmt("show streams;")[0]
        return [t["name"] for t in json["streams"]]


    def list_type_names(self) -> list[str]:
        json = self.stmt("show types;")[0]
        return json["types"].keys()


    def list_table_names(self) -> list[str]:
        json = self.stmt("show tables;")[0]
        return [t["name"] for t in json["tables"]]


    def list_connector_names(self) -> list[str]:
        json = self.stmt("show connectors;")[0]
        return [t["name"] for t in json["connectors"]]

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
