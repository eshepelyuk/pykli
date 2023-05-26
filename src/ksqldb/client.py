import asyncio

from ksqldb.api import BaseAPI


class KSQLdbClient:
    def __init__(self, url, api_key=None, api_secret=None):
        self.url = url
        self.api = BaseAPI(url, api_key, api_secret)

    def get_properties(self):
        properties = self.api.ksql("show properties;")
        return properties[0]["properties"]

    def ksql(self, ksql_string, stream_properties=None):
        return self.api.ksql(ksql_string, stream_properties=stream_properties)

    def ksql_async(self, ksql_string, stream_properties=None):
        return self.api.ksql_async(ksql_string, stream_properties=stream_properties)

    @staticmethod
    async def get_query_result(results):
        results_list = [x async for x in results]
        return results_list

    def query_sync(self, query_string, stream_properties=None, timeout=10):
        assert (
            "emit changes" not in query_string.lower()
        ), "EMIT CHANGES can only be used asynchronously, please use query_async"

        return asyncio.run(
            self.get_query_result(
                self.api.query(
                    query_string=query_string,
                    timeout=timeout,
                    stream_properties=stream_properties,
                )
            )
        )

    async def query_async(self, query_string, stream_properties=None, timeout=10):
        async for x in self.api.query(
            query_string=query_string,
            timeout=timeout,
            stream_properties=stream_properties,
        ):
            yield x

    def close_query(self, query_id):
        return self.api.close_query(query_id)

    def inserts_stream(self, stream_name, rows):
        return self.api.inserts_stream(stream_name, rows)
