import asyncio
import pathlib
from typing import List, Dict, Optional, Union

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
        video_card_list = [await self._page_parser.parse_video_card(video_card_elem) for video_card_elem in
                           video_card_elem_list]

        return video_card_list

    @classmethod
    async def parallel_crawl(cls,
                             search_term_list: List[str],
                             n_target_list: List[int],
                             output_dir: Union[pathlib.Path, str],
                             filter_options_list: Optional[List[Dict]] = None,
                             n_workers: int = 1,
                             verbose: bool = False) -> None:
        """
        Parallel crawl function for YoutubeVideoInfoCrawler.

        :param search_term_list: List of search terms.
        :param n_target_list: List of target number of results.
        :param filter_options_list: List of filter options.
        :param n_workers: Number of parallel workers.
        :param output_dir: Directory to store the output data.
        :param verbose: Whether to print the log.
        """
        # 1. Parameter validation: param list must have the same length
        if filter_options_list is None:
            filter_options_list = [None] * len(search_term_list)
        assert len(search_term_list) == len(n_target_list) == len(filter_options_list), "Lengths of the lists must be the same."
        n = len(search_term_list)

        # 2. Create task parameters
        task_params = [
            {
                "log_filename_func": lambda **kwargs: f"{kwargs['search_term']}_{kwargs['n_target']}_video_info.log",
                "data_filename_func": lambda **kwargs: f"{kwargs['search_term']}_{kwargs['n_target']}_video_info.csv",
                "output_dir": output_dir,
                "verbose": verbose,
                # children class specific parameters
                "search_term": search_term_list[i],
                "n_target": n_target_list[i],
                "filter_options": filter_options_list[i],
            }
            for i in range(n)
        ]
        await cls._parallel_crawl_base(worker_fn=cls._generic_worker, task_params=task_params, n_workers=n_workers)


__all__ = ["YoutubeVideoInfoCrawler"]
