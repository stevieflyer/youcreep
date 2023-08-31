import pathlib

from wrightyrion.agent import Agent

from .modules import ShortPageHandler, CommonPageHandler, VideoPageHandler, SearchPageHandler
from .url_parser import YoutubeUrlParser, YouTubeUrlType


class YoutubeAgent(Agent):
    home_url = "https://www.youtube.com/"

    def _init_hook(self) -> None:
        self._common_hdl = CommonPageHandler(agent=self, debug_tool=self.debug_tool)
        self._short_hdl = ShortPageHandler(agent=self, debug_tool=self.debug_tool)
        self._video_hdl = VideoPageHandler(agent=self, debug_tool=self.debug_tool)
        self._search_hdl = SearchPageHandler(agent=self, debug_tool=self.debug_tool)

    async def _start_hook(self) -> None:
        await self.browser_mgr.go(self.home_url)

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
    def short_hdl(self) -> ShortPageHandler:
        return self._short_hdl

    @property
    def video_hdl(self) -> VideoPageHandler:
        return self._video_hdl

    @property
    def search_hdl(self) -> SearchPageHandler:
        return self._search_hdl


__all__ = ['YoutubeAgent']
