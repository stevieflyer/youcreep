import pathlib
from typing import Dict

from ._base_crawler import YoutubeBaseCrawler
from .page_parser.modules import YoutubeUrlParser


class YoutubeCommentCrawler(YoutubeBaseCrawler):
    """
    Crawler for video comments on YouTube.
    """
    async def crawl(self, video_url: str, n_target: (int, None) = None, ret_meta_info: bool = False):
        """
        Crawl the comments from the video page.

        :param video_url: (str) The URL of the video to crawl comments from.
        :param n_target: (int) target number of comments, which may not be reached. If None, all comments will be crawled.
        :param ret_meta_info: (bool) Whether to return the meta info of the video.
        """
        assert YoutubeUrlParser.is_video_url(video_url) is True, "The url is not a video url."

        await self._browser_agent.go(video_url)

        # load the search result
        comment_card_list = await self._browser_agent.scroll_load_comments(n_target=n_target)

        await self._browser_agent.dismiss_premium_modal()

        # get meta info
        meta_info = await self._page_parser.parse_video_page_meta_info()
        self._browser_agent.debug_tool.info(f"View Count: {meta_info['view_count']}, Comment Count: {meta_info['comment_count']}")

        # Parse and get the video info
        comment_list = [await self._page_parser.parse_video_comment(comment_card) for comment_card in comment_card_list]

        if ret_meta_info:
            return comment_list, ret_meta_info
        else:
            return comment_list

    @classmethod
    def required_fields(cls) -> Dict:
        """
        - `video_url`: str, The URL of the video to crawl comments from.
        - `n_target`: int, target number of comments, which may not be reached. If None, all comments will be crawled.
        - `output_dir`: Union[pathlib.Path, str]
        """
        return {
            "video_url": str,
            "n_target": (int, type(None)),
            "output_dir": (pathlib.Path, str),
        }

    @classmethod
    def optional_fields(cls) -> Dict:
        """No optional fields."""
        return {}

    @classmethod
    def _save_name(cls, _kw: dict) -> str:
        """The save name for the crawler."""
        video_id = YoutubeUrlParser.parse_url(_kw["video_url"])["video_id"]
        return f"{video_id}_{_kw['n_target']}_comment"


__all__ = ["YoutubeCommentCrawler"]
