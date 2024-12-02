import abc

import httpx


class BaseClient(abc.ABC):
    client: httpx.AsyncClient

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @property
    @abc.abstractmethod
    def root_url(self) -> str:
        """Abstract property, override"""
