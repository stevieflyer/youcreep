import pathlib
import time
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

        await self._browser_agent.go_video_page(video_url=video_url)

        # Get the meta info of the video
        meta_info = await self._page_parser.parse_video_page_meta_info()
        self._browser_agent.debug_tool.info(f"View Count: {meta_info['view_count']}, Comment Count: {meta_info['comment_count']}")

        if n_target is not None:
            n_target = min(n_target, meta_info["comment_count"])

        self._browser_agent.debug_tool.info(f"Start loading comments by scrolling...n_target = {n_target}")
        before_scroll = time.time()
        # Scroll and load all comments
        comment_card_list = await self._browser_agent.scroll_load_comments(n_target=n_target)
        self._browser_agent.debug_tool.info(f"Loading comments finished, time elapsed: {time.time() - before_scroll:.2f}s, loading {len(comment_card_list)} comments. Avg: {(time.time() - before_scroll) / len(comment_card_list):.2f}s/comment.")

        # Parse and get the video info
        self._browser_agent.debug_tool.info(f"Start parsing the comment cards...")
        before_parse = time.time()
        comment_list = [await self._page_parser.parse_video_comment(comment_card) for comment_card in comment_card_list]
        self._browser_agent.debug_tool.info(f"Parsing comments finished, time elapsed: {time.time() - before_parse:.2f}s, parsing {len(comment_list)} comments. Avg: {(time.time() - before_parse) / len(comment_list):.2f}s/comment.")

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
