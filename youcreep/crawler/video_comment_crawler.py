import pathlib
from typing import Union

from gembox.io import check_and_make_dir

from .base_crawler import YoutubeBaseCrawler
from youcreep.common import YoutubeUrlParser
from ..browser_agent.url_parser import YouTubeUrlType


class YoutubeCommentCrawler(YoutubeBaseCrawler):
    async def crawl(self, video_url: str, save_dir: Union[str, pathlib.Path], n_target: Union[int, None] = None):
        """
        Crawl the video info from YouTube search result page.

        :param video_url: (str) The target video_url
        :param n_target: (int) Target number of results, which may not be reached. If None, all results will be crawled.
        :param save_dir: (str, pathlib.Path) the directory to save the video info

        :return: (None)
        """
        if self.is_running is False:
            raise RuntimeError("Please start the crawler first.")
        save_dir = check_and_make_dir(save_dir)

        parsed_result = YoutubeUrlParser.parse_url(video_url)
        url_type = parsed_result['type']
        assert url_type == YouTubeUrlType.SHORT or url_type == YouTubeUrlType.VIDEO, f"Invalid url type: {url_type}, it should be either SHORT or VIDEO."

        # go to the target video page
        await self.browser_agent.go_youtube_page(url=video_url)

        # load the comment
        if url_type == YouTubeUrlType.VIDEO:
            await self.browser_agent.video_hdl.scroll_load_comment_cards(n_target=n_target)
        else:
            raise NotImplementedError(f"Short video comment crawler is not implemented yet.")

        # save to the disk
        save_name = f"{self._file_name(video_url=video_url, n_target=n_target)}.html"
        await self.browser_agent.download_page(file_path=save_dir / save_name)

    @classmethod
    def _file_name(cls, **kwargs) -> str:
        video_url = kwargs.pop("video_url")
        n_target = kwargs.pop("n_target", None)

        parsed_result = YoutubeUrlParser.parse_url(video_url)
        video_type, video_id = parsed_result['type'], parsed_result['video_id']

        return f"{video_id}_{n_target}_{video_type.value}_video"

    @classmethod
    def required_fields(cls) -> dict:
        return {
            "video_url": str,
            "save_dir": (str, pathlib.Path),
        }

    @classmethod
    def optional_fields(cls) -> dict:
        return {
            "n_target": (int, type(None)),
        }


__all__ = ['YoutubeCommentCrawler']
