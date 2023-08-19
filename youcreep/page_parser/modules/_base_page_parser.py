import abc
from typing import Any

import pyppeteer.element_handle

from zephyrion.pypp import PyppeteerAgent


class BaseParserHandler(abc.ABC):
    """
    Base parser handler interface for parsing page elements.
    """
    def __init__(self, agent: PyppeteerAgent):
        self.agent = agent

    @abc.abstractmethod
    async def parse(self, element: pyppeteer.element_handle.ElementHandle) -> Any:
        pass


__all__ = ["BaseParserHandler"]
