import pathlib

from gembox.io import check_and_make_dir

from .base_crawler import YoutubeBaseCrawler


class YoutubeVideoInfoCrawler(YoutubeBaseCrawler):
    async def crawl(self, search_term: str, n_target: int, save_dir: (str, pathlib.Path), filter_options: dict = None):
        """
        Crawl the video info from YouTube search result page.

        :param search_term: (str) The search term.
        :param n_target: (int) Target number of results, which may not be reached. If None, all results will be crawled.
        :param save_dir: (str, pathlib.Path) the directory to save the video info
        :param filter_options: (dict) Filter options for the search result.
        :return: (List[VideoInfo]) the video info list
        """
        if self.is_running is False:
            raise RuntimeError("Please start the crawler first.")
        save_dir = check_and_make_dir(save_dir)

        # search for the search term
        await self.browser_agent.search(search_term=search_term)

        # filter the search result
        for filter_section, filter_option in filter_options.items():
            await self.browser_agent.search_hdl.filter_search_result(filter_section=filter_section,
                                                                     filter_option=filter_option)

        # load the search result
        await self.browser_agent.search_hdl.scroll_load_video_cards(n_target=n_target)

        # save to the disk
        save_name = f"{self._file_name(search_term=search_term, n_target=n_target, filter_options=filter_options)}.html"
        await self.browser_agent.download_page(file_path=save_dir / save_name)

    @classmethod
    def _file_name(cls, **kwargs) -> str:
        search_term = kwargs.pop("search_term")
        n_target = kwargs.pop("n_target")
        filter_options = kwargs.pop("filter_options", None)

        if filter_options is not None:
            filter_str = "_".join([str(filter_option.value) for filter_option in filter_options.values()])
        else:
            filter_str = "NoOption"

        file_name = f"{search_term}_{n_target}_{filter_str}_search"
        return file_name

    @classmethod
    def required_fields(cls) -> dict:
        return {
            "search_term": str,
            "n_target": int,
            "save_dir": (str, pathlib.Path),
        }

    @classmethod
    def optional_fields(cls) -> dict:
        return {
            "filter_options": (dict, type(None)),
        }


__all__ = ['YoutubeVideoInfoCrawler']
