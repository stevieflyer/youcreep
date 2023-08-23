import abc

from zephyrion.pypp import PyppeteerAgent


class BaseParserHandler(abc.ABC):
    """
    Base parser handler interface for parsing page elements.
    """
    def __init__(self, agent: PyppeteerAgent):
        self.agent = agent


__all__ = ["BaseParserHandler"]
