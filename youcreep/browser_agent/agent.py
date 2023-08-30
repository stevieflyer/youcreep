import pathlib

from wrightyrion.agent import Agent
from gembox.debug_utils import Debugger
from wrightyrion.browser_mgr import SingleBrowserManager
from wrightyrion.data_extractor import DataExtractor
from wrightyrion.page_interactor import PageInteractor

from .modules import ShortPageHandler, CommonPageHandler, VideoPageHandler, SearchPageHandler
from .url_parser import YoutubeUrlParser, YouTubeUrlType


class YoutubeAgent:
    home_url = "https://www.youtube.com/"

    def __init__(self, agent: Agent, headless: bool, debug_tool: Debugger):
        assert isinstance(agent, Agent), f"agent must be a `wrightyrion.agent.Agent`, but {type(agent)}"
        self._agent = agent
        self._headless = headless
        self._debug_tool = debug_tool if debug_tool is not None else Debugger()
        self._common_hdl = CommonPageHandler(agent=agent, debug_tool=debug_tool)
        self._short_hdl = ShortPageHandler(agent=agent, debug_tool=debug_tool)
        self._video_hdl = VideoPageHandler(agent=agent, debug_tool=debug_tool)
        self._search_hdl = SearchPageHandler(agent=agent, debug_tool=debug_tool)

    @classmethod
    async def instantiate(cls, headless=False, debug_tool: Debugger = None) -> "YoutubeAgent":
        debug_tool = debug_tool if debug_tool is not None else Debugger()
        agent = await Agent.instantiate(headless=headless, debug_tool=debug_tool)
        instance = cls(agent=agent, headless=headless, debug_tool=debug_tool)
        return instance

    async def start(self) -> 'YoutubeAgent':
        if self.is_running:
            self.debug_tool.warn("YoutubeAgent is already running. No need to start again")
            return self

        self.debug_tool.info(f"Starting YoutubeAgent...")
        await self._agent.start()
        await self.browser_mgr.go(self.home_url)
        self.debug_tool.info(f"Starting YoutubeAgent Successfully")
        return self

    async def stop(self) -> 'YoutubeAgent':
        if self.is_running is False:
            self.debug_tool.warn("YoutubeAgent is not running. No need to close")
            return self

        self.debug_tool.info(f"Closing YoutubeAgent...")
        await self._agent.stop()
        self.debug_tool.info(f"Closing YoutubeAgent Successfully")
        return self

    async def search(self, search_term: str):
        """
        Search the search term in the search bar.

        @in-page: any YouTube page
        @out-page: search result page

        :param search_term: (str) the search term
        :return:
        """
        return await self._common_hdl.search(search_term=search_term)

    async def download_page(self, file_path: (str, pathlib.Path), encoding="utf-8"):
        """
        Download current web page. Save to the file system.

        :param file_path: (str, pathlib.Path) the file path to save the web page
        :param encoding: (str) the file encoding, default is 'utf-8'
        :return:
        """
        return await self._common_hdl.download_page(file_path=file_path, encoding=encoding)

    async def go_youtube_page(self, url: str):
        """
        Go to a YouTube page, and initialize the page.

        :param url: (str) the url of the YouTube page
        :return: (None)
        """
        parsed_result = YoutubeUrlParser.parse_url(url)
        url_type: YouTubeUrlType = parsed_result["type"]
        if url_type == YouTubeUrlType.VIDEO:
            await self._video_hdl.go_video_page(url=url)
        elif url_type == YouTubeUrlType.SHORT:
            await self._short_hdl.go_short_page(url=url)
        else:
            await self.browser_mgr.go(url=url)

    # getters
    @property
    def headless(self) -> bool:
        return self._headless

    @property
    def debug_tool(self) -> Debugger:
        return self._debug_tool

    @property
    def short_hdl(self) -> ShortPageHandler:
        return self._short_hdl

    @property
    def video_hdl(self) -> VideoPageHandler:
        return self._video_hdl

    @property
    def search_hdl(self) -> SearchPageHandler:
        return self._search_hdl

    @property
    def is_running(self) -> bool:
        return self._agent.is_running

    @property
    def page_interactor(self) -> PageInteractor:
        return self._agent.page_interactor

    @property
    def data_extractor(self) -> DataExtractor:
        return self._agent.data_extractor

    @property
    def browser_mgr(self) -> SingleBrowserManager:
        return self._agent.browser_mgr


__all__ = ['YoutubeAgent']
