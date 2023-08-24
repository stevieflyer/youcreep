import pyppeteer.element_handle

from ..dao.pojo import VideoInfo, VideoComment
from ..browser_agent import YoutubeBrowserAgent
from .modules import SearchResultPageParser, VideoPageParser, YoutubeUrlParser


class YoutubePageParser:
    """
    The page parser for YouTube.

    `YoutubePageParser` is a class that handles how to parse the website page of YouTube.
    Currently, the parser relies on `pyppeteer` module to support efficient element manipulation.
    """
    def __init__(self, browser_agent: YoutubeBrowserAgent):
        self._video_info_parser = SearchResultPageParser(agent=browser_agent)
        self._video_comment_parser = VideoPageParser(agent=browser_agent)

    async def parse_video_card(self, video_card: pyppeteer.element_handle.ElementHandle) -> VideoInfo:
        """
        Parse the video card element to get the video info.

        :param video_card: (pyppeeteer.element_handle.ElementHandle) the video card element
        :return: (VideoInfo) the video info
        """
        return await self._video_info_parser.parse(video_card)

    async def parse_video_page_meta_info(self) -> dict:
        """
        Parse the video page to get the meta info.

        :return: (dict) the meta info
        """
        if not YoutubeUrlParser.is_video_url(self._video_comment_parser.agent.url):
            raise ValueError(f"The url {self._video_comment_parser.agent.url} is not a video url.")
        return await self._video_comment_parser.parse_meta_info()

    async def parse_video_comment(self, comment: pyppeteer.element_handle.ElementHandle) -> VideoComment:
        """
        Parse the video comment element to get the comment text.

        :param comment: (pyppeeteer.element_handle.ElementHandle) the video comment element
        :return: (str) the comment text
        """
        return await self._video_comment_parser.parse_comment_card_test(comment)


__all__ = ["YoutubePageParser"]
