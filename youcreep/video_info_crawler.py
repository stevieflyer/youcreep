import asyncio
import pathlib
from typing import List, Dict

from .dao.pojo import VideoInfo
from ._base_crawler import YoutubeBaseCrawler


class YoutubeVideoInfoCrawler(YoutubeBaseCrawler):
    """
    Crawler for video infos on YouTube.

    This crawler crawls the video infos from YouTube search result page.
    """

    async def crawl(self, search_term: str, n_target: int, filter_options: dict = None) -> List[VideoInfo]:
        """
        Crawl the video infos from YouTube search result page.

        :param search_term: (str) The search term.
        :param n_target: (int) Target number of results, which may not be reached. If None, all results will be crawled.
        :param filter_options: (dict) Filter options for the search result.
        """
        # search for the search term
        await self._browser_agent.search(search_term=search_term)
        # filter the search result
        if filter_options is not None:
            for filter_section, filter_option in filter_options.items():
                self._browser_agent.debug_tool.info(
                    f"Filtering the search result by {filter_section} -> {filter_option}")
                await self._browser_agent.filter_search_result(filter_section=filter_section,
                                                               filter_option=filter_option)
                # wait for the page to load
                # TODO: find a better way to wait for the page to load, e.g. wait for the element to appear
                await asyncio.sleep(1.5)  # Use asyncio.sleep instead of time.sleep

        # load the search result
        video_card_elem_list = await self._browser_agent.scroll_load_video_cards(n_target=n_target)
        # Parse and get the video info
        self._browser_agent.debug_tool.info(f"Start parsing the video cards...")
        video_card_list = [await self._page_parser.parse_video_card(video_card_elem) for video_card_elem in
                           video_card_elem_list]

        # if crawl_details:
        #     self._browser_agent.debug_tool.info(f"Start crawling the video details...")
        #     for video_card in video_card_list:
        #         new_video_card_dict: dict = await self._crawl_video_meta_info(video_card.to_dict())
        #         video_card.view_count = new_video_card_dict['view_count']
        #         video_card.comment_count = new_video_card_dict['comment_count']

        return video_card_list

    # async def _crawl_video_meta_info(self, video_info: dict):
    #     self._browser_agent.debug_tool.info(f"Crawling the video meta info of {video_info['video_id']}...")
    #     url = video_info["video_url"]
    #     await self._browser_agent.go(url)
    #     meta_info: dict = await self._page_parser.parse_video_page_meta_info()
    #     # update the video card by meta_info
    #     video_info["view_count"] = meta_info["view_count"]
    #     video_info["comment_count"] = meta_info["comment_count"]
    #     return video_info

    @classmethod
    def required_fields(cls) -> Dict:
        """
        - `search_term`: str
        - `n_target`: int, target number of results, which may not be reached. If None, all results will be crawled.
        - `output_dir`: Union[pathlib.Path, str]
        """
        return {
            "search_term": str,
            "n_target": (int, type(None)),
            "output_dir": (pathlib.Path, str),
        }

    @classmethod
    def optional_fields(cls) -> Dict:
        """
        - `filter_options`: dict, filter options for the search result.

        e.g.
        ```python
        {
            FilterSection.LENGTH: FilterLengthOption.MEDIUM,
            FilterSection.ORDER_BY: FilterOrderByOption.VIEW_COUNT
        }
        ```
        """
        return {
            "filter_options": (dict, None),
        }

    @classmethod
    def _save_name(cls, _kw: dict) -> str:
        return f"{_kw['search_term']}_{_kw['n_target']}_video_info"


__all__ = ["YoutubeVideoInfoCrawler"]
