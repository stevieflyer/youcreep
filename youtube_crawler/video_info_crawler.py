from typing import List

from .dao.pojo import VideoInfo
from ._base_crawler import YoutubeBaseCrawler


class YoutubeVideoInfoCrawler(YoutubeBaseCrawler):
    """
    Crawler for video infos on YouTube.

    This crawler crawls the video infos from YouTube search result page.
    """
    async def crawl(self, search_term: str, n_target: int, filter_options: dict = None) -> List[VideoInfo]:
        # search for the search term
        await self._browser_agent.search(search_term=search_term)
        # filter the search result
        if filter_options is not None:
            for filter_section, filter_option in filter_options.items():
                await self._browser_agent.filter_search_result(filter_section=filter_section, filter_option=filter_option)
        # load the search result
        video_card_elem_list = await self._browser_agent.scroll_load_video_cards(n_target=n_target)
        # Parse and get the video info
        video_card_list = [await self._page_parser.parse_video_card(video_card_elem) for video_card_elem in video_card_elem_list]

        return video_card_list


__all__ = ["YoutubeVideoInfoCrawler"]
