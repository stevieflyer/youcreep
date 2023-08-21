import pathlib
from typing import List, Union

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

    @classmethod
    async def parallel_crawl(cls,
                             video_url_list: List[str],
                             n_target_list: List[int],
                             output_dir: Union[pathlib.Path, str],
                             n_workers: int = 1,
                             verbose: bool = False) -> None:
        """
        Parallel crawl function for YoutubeVideoInfoCrawler.

        :param video_url_list: List of video urls.
        :param n_target_list: List of target number of results.
        :param n_workers: Number of parallel workers.
        :param output_dir: Directory to store the output data.
        :param verbose: Whether to print the log.
        """
        # 1. Parameter validation: param list must have the same length
        assert len(video_url_list) == len(n_target_list), "Lengths of the lists must be the same."
        n = len(video_url_list)

        # 2. Create task parameters
        task_params = [
            {
                "log_filename_func": lambda **kwargs: f"{YoutubeUrlParser.parse_url(kwargs['video_url'])['video_id']}_{kwargs['n_target']}_comment.log",
                "data_filename_func": lambda **kwargs: f"{YoutubeUrlParser.parse_url(kwargs['video_url'])['video_id']}_{kwargs['n_target']}_comment.csv",
                "output_dir": output_dir,
                "verbose": verbose,
                # children class specific parameters
                "video_url": video_url_list[i],
                "n_target": n_target_list[i],
            }
            for i in range(n)
        ]
        await cls._parallel_crawl_base(worker_fn=cls._generic_worker, task_params=task_params, n_workers=n_workers)


__all__ = ["YoutubeCommentCrawler"]
