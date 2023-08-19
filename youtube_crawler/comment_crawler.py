from typing import List

from .dao.pojo import VideoComment
from ._base_crawler import YoutubeBaseCrawler
from .page_parser.modules import YoutubeUrlParser


class YoutubeCommentCrawler(YoutubeBaseCrawler):
    """
    Crawler for video comments on YouTube.
    """
    async def crawl(self, video_url: str, n_target: int = None) -> List[VideoComment]:
        assert YoutubeUrlParser.is_video_url(video_url) is True, "The url is not a video url."

        await self._browser_agent.go(video_url)

        # load the search result
        comment_card_list = await self._browser_agent.scroll_load_comments(n_target=n_target)

        # Parse and get the video info
        comment_list = [await self._page_parser.parse_video_comment(comment_card) for comment_card in comment_card_list]

        return comment_list


__all__ = ["YoutubeCommentCrawler"]
