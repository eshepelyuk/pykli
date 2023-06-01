import base64
import httpx

def is_stmt(s):
    return (s.startswith("show") or
        s.startswith("list") or s.startswith("describe") or
        s.startswith("drop")
        )

class KsqlDBClient:
    def __init__(self, url, api_key=None, api_secret=None):
        # TODO introduce common headers
        self._headers = {"Content-Type": "application/vnd.ksql.v1+json"}
        self._client = httpx.Client(base_url=url, http2=True)

        if api_key and api_secret:
            b64string = base64.b64encode(bytes(f"{api_key}:{api_secret}"))
            self._headers["Authorization"] = f"Basic {b64string}"

    async def info(self):
        pass

    def stmt(self, ksql_str, stream_props={}):
        body = {
            "ksql": ksql_str,
            "streamsProperties": stream_props,
        }
        r = self._client.post("/ksql", json=body, headers=self._headers)
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
