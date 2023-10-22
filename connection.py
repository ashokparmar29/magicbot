import weaviate
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data
from weaviate.client import Client
from typing import Optional


class WeaviateConnection(ExperimentalBaseConnection["Client"]):
    def __init__(
        self,
        connection_name: str,
        url=None,
        api_key=None,
        additional_headers=None,
        **kwargs,
    ) -> None:
        self.url = url
        self.api_key = api_key
        self.additional_headers = additional_headers
        super().__init__(connection_name, **kwargs)

    def _connect(self, **kwargs) -> Client:
        auth_config = self._create_auth_config()
        url = self.url or self._secrets.get("WEAVIATE_URL")
        return Client(
            url,
            auth_client_secret=auth_config,
            additional_headers=self.additional_headers,
        )
    
    
    def _create_auth_config(self) -> Optional[weaviate.AuthApiKey]:
        api_key = self.api_key or self._secrets.get("WEAVIATE_API_KEY")
        if api_key is not None:
            return weaviate.AuthApiKey(api_key=api_key)
        else:
            return None

    def client(self) -> Client:
        return self._connect()