import asyncio
import pathlib
import aiofiles
from typing import Union

from gembox.io import check_and_make_dir

from youcreep.browser_agent.modules import VideoPageHandler, ShortPageHandler
from youcreep.common import YoutubeUrlParser, YouTubeUrlType
from youcreep.crawler.base_crawler import YoutubeBaseCrawler


class YoutubeCommentCrawler(YoutubeBaseCrawler):
    async def _crawl(self,
                     video_url: str,
                     save_dir: Union[str, pathlib.Path],
                     n_target: Union[int, None] = None) -> None:
        """
        Crawl the video info from YouTube search result page.

        :param video_url: (str) The target video_url
        :param n_target: (int) Target number of results, which may not be reached. If None, all results will be crawled.
        :param save_dir: (str, pathlib.Path) the directory to save the video info

        :return: (None)
        """
        save_dir = check_and_make_dir(save_dir)

        parsed_result = YoutubeUrlParser.parse_url(video_url)
        url_type = parsed_result['type']
        assert url_type == YouTubeUrlType.SHORT or url_type == YouTubeUrlType.VIDEO, f"Invalid url type: {url_type}, it should be either SHORT or VIDEO."
        handler: Union[VideoPageHandler, ShortPageHandler] = self.browser_agent.video_hdl if url_type == YouTubeUrlType.VIDEO else self.browser_agent.short_hdl

        # Step 1: go to the target video page
        n_retry, max_retry = 0, 3
        while True:
            await self.browser_agent.go_youtube_page(url=video_url)
            await asyncio.sleep(1)  # 等待 meta info 区域的出现

            # Step 2: 获取 meta info
            meta_info = await handler.parse_meta_info()
            # FIXME: meta_info["comment_count"] could be NoneType
            n_comments = int(meta_info['comment_count'])
            if n_target is None:
                n_target = n_comments
            else:
                n_target = min(n_target, n_comments)
            self.debug_tool.info(f"Meta Info is parsed: {meta_info}, we set n_target to {n_target}")

            # Step 2.(1) 如果没有 comment, 直接返回
            if n_target == 0:
                self.debug_tool.info(f"No comment is found for {video_url}, skip.")
                # 写一个空文件
                save_name = f"EMPTY_{self._crawler_args_str(video_url=video_url, n_target=n_target)}.html"
                async with aiofiles.open(save_dir / save_name, mode='w', encoding='utf-8') as f:
                    await f.write("")
                self.debug_tool.info(f"Empty file is saved to {save_dir / save_name}")
                return

            # Step 2.(2) 如果有 comment, 则开始爬取
            comments = await handler.scroll_load_comment_cards(n_target=n_target)

            if len(comments) > 0 and len(comments) >= int(n_target * 0.7):
                self.debug_tool.info(f"Finally, we loaded {len(comments)} comments, n_target: {n_target}.")
                save_name = f"{self._crawler_args_str(video_url=video_url, n_target=n_target)}.html"
                await self.browser_agent.download_page(file_path=save_dir / save_name)
                break
            else:
                n_retry += 1
                self.debug_tool.warn(f"Finally, we loaded {len(comments)} comments, n_target: {n_target}. Which is not enough(no less than 70%).")
                self.debug_tool.warn(f"Retry {n_retry} times...")
                if n_retry >= max_retry:
                    # 如果试了 max_retry 次, 都没有加载到足够的 comments, 则保存当前页面
                    self.debug_tool.error(f"Retry {n_retry} times, but we cannot load enough comments, n_target: {n_target}.")
                    save_name = f"NOTENOUGH_{self._crawler_args_str(video_url=video_url, n_target=n_target)}.html"
                    await self.browser_agent.download_page(file_path=save_dir / save_name)
                    break

        self.debug_tool.info(f"YoutubeCommentCrawler crawling finished.")

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

    @classmethod
    def _crawler_args_str(cls, **kwargs) -> str:
        video_url = kwargs.pop("video_url")
        n_target = kwargs.pop("n_target", None)

        parsed_result = YoutubeUrlParser.parse_url(video_url)
        video_type, video_id = parsed_result['type'], parsed_result['video_id']

        return f"{video_id}_{n_target}_{video_type.value}_video"


__all__ = ['YoutubeCommentCrawler']
