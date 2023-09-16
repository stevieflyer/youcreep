from abc import ABC

from wrightyrion.base_class import BaseCrawler

from youcreep.browser_agent import YoutubeAgent


class YoutubeBaseCrawler(BaseCrawler, ABC):
    """
    Crawler for video info on YouTube.

    Crawler is responsible for interacting with the browser, save the webpage and parse the webpage to get data.
    """
    agent_cls = YoutubeAgent

    # the following is for type hinting
    @property
    def browser_agent(self) -> YoutubeAgent:
        return self._browser_agent
