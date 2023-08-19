import abc
import pathlib
from typing import Union

from gembox.debug_utils import Debugger

from youcreep.page_parser import YoutubePageParser
from youcreep.browser_agent import YoutubeBrowserAgent


class YoutubeBaseCrawler:
    def __init__(self, headless=False, debug_tool: Debugger = None, interactor_config_path: Union[str, pathlib.Path] = None):
        self._browser_agent = YoutubeBrowserAgent(headless=headless, debug_tool=debug_tool, interactor_config_path=interactor_config_path)
        self._page_parser = YoutubePageParser(browser_agent=self._browser_agent)

    @property
    async def is_running(self):
        page = await self._browser_agent.browser_manager.get_page()
        return self._browser_agent.is_running and page is not None

    async def start(self) -> None:
        await self._browser_agent.start()

    async def stop(self) -> None:
        await self._browser_agent.stop()

    @abc.abstractmethod
    def crawl(self, *args, **kwargs):
        raise NotImplementedError


__all__ = ["YoutubeBaseCrawler"]
