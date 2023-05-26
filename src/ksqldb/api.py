import base64
import json
import httpx


class BaseAPI:
    def __init__(self, url, api_key=None, api_secret=None):
        self.url = url
        self.headers = {"Content-Type": "application/vnd.ksql.v1+json"}
        if api_key and api_secret:
            b64string = base64.b64encode(bytes(f"{api_key}:{api_secret}"))
            self.headers["Authorization"] = f"Basic {b64string}"

    def ksql(self, ksql_string, stream_properties=None):
        body = {
            "ksql": ksql_string,
            "streamsProperties": stream_properties if stream_properties else {},
        }
        r = httpx.post(f"{self.url}/ksql", json=body, headers=self.headers)
        r.raise_for_status()
        return r.json()

    async def ksql_async(self, ksql_string, stream_properties=None):
        body = {
            "ksql": ksql_string,
            "streamsProperties": stream_properties if stream_properties else {},
        }

        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self.url}/ksql", json=body, headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def query(self, query_string, timeout, stream_properties=None):
        body = {
            "sql": query_string,
            "properties": stream_properties if stream_properties else {},
        }

        client = httpx.AsyncClient(http1=False, http2=True)
        async with client.stream("POST", f"{self.url}/query-stream", json=body, timeout=timeout) as r:
            async for line in r.aiter_lines():
                yield json.loads(line)

    def close_query(self, query_id):
        response = httpx.post(f"{self.url}/close-query", json={"queryId": query_id})
        return response.ok

    def inserts_stream(self, stream_name, rows):
        body = json.dumps({"target": stream_name}) + "\n"
        for row in rows:
            body += f"{json.dumps(row)}\n"

        client = httpx.Client(http1=False, http2=True)
        with client.stream("POST", f"{self.url}/inserts-stream", content=body, headers=self.headers) as r:
            response_data = [json.loads(x) for x in r.iter_lines()]

        return response_data
