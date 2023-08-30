import abc
from typing import Union

from gembox.debug_utils import Debugger
from wrightyrion.agent import Agent
from ..url_parser import YoutubeUrlParser, YouTubeUrlType


class PageHandler(abc.ABC):
    """
    PageHandler is a base class for all page handlers.

    PageHandler is responsible for handling one type of page. Multiple PageHandlers can form up a wrightyrion agent.
    """
    page_type: Union[None, YouTubeUrlType] = None

    def __init__(self, agent: Agent, debug_tool: Debugger):
        assert isinstance(agent, Agent), f"agent must be a `wrightyrion.agent.Agent`, but {type(agent)}"
        self.agent = agent
        self.debug_tool = debug_tool

    def check_url(self, test_url: str = None) -> bool:
        """
        Check whether the current url is the expected type.

        :return: (bool) True when the url is acceptable
        """
        if self.page_type is None:
            return True
        url: str = self.agent.page.url if test_url is None else test_url
        url_type: YouTubeUrlType = YoutubeUrlParser.parse_url(url)["type"]
        if url_type != self.page_type:
            self.debug_tool.warn(f"Page type is {url_type}, but expected {self.page_type}")
            return False
        return True


__all__ = ['PageHandler']
