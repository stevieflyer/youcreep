import asyncio
import playwright.async_api
from typing import List, Callable

from gembox.re_utils import search_comma_sep_num

from youcreep.browser_agent.modules.page_handler import PageHandler
from youcreep.browser_agent.url_parser import YouTubeUrlType
from youcreep.common.selectors.common_sels import dismiss_btn_sel, comment_card_sel
from youcreep.common.selectors.video_page_sels import view_count_sel, comment_count_sel


class VideoPageHandler(PageHandler):
    page_type = YouTubeUrlType.VIDEO

    async def go_video_page(self, url: str):
        """
        Go to a video page, and initialize the page.

        :param url: (str) the url of the video page
        :return: (None)
        """
        if not self.check_url(test_url=url):
            self.debug_tool.warn(f"Cannot go to video page, because the page is not a video page, current url: {self.agent.page.url}")
            return

        self.debug_tool.info(f"Going to video page {url}...")
        await self.agent.browser_mgr.go(url)

        # Initialization at a video page
        self.debug_tool.info(f"Initial Scrolling to load meta info")
        initial_scroll, scroll_step = 6, 500
        for _ in range(initial_scroll):
            # scroll by `scroll_step`
            await asyncio.sleep(0.6)
            await self.agent.page.evaluate(f"window.scrollBy(0, {scroll_step})")
        self.debug_tool.info(f"Initial Scrolling finished after {initial_scroll} times scrolling, step: {scroll_step}")

        await asyncio.sleep(1)
        await self._dismiss_popup_if_exist()

    async def _dismiss_popup_if_exist(self):
        """
        Dismiss the popup if it exists.

        :return: (None)
        """
        if await self.agent.page.is_visible(dismiss_btn_sel):
            await self.agent.page.click(dismiss_btn_sel)
            self.debug_tool.info(f"Dismiss button clicked")

    async def scroll_load_comment_cards(self, n_target: int, callbacks: List[Callable] = None) -> List[playwright.async_api.ElementHandle]:
        """
        Scroll down to load more comment cards.

        @in_page: video page

        @out_page: video page

        :param n_target: (int) The target number of comment cards to load.
        :param callbacks: (List[Callable]) The callback function to call after each scroll step.
        :return: (List[ElementHandle]) The list of comment card elements.
        """
        assert isinstance(callbacks, (list, set, tuple, type(None))), f"callbacks should be a list, but got {type(callbacks)}"

        meta_info = await self._parse_meta_info()
        n_comments = meta_info["comment_count"]
        if n_target is None:
            n_target = n_comments
        else:
            n_target = min(n_target, n_comments)
        callbacks = [] if callbacks is None else list(callbacks)
        callbacks.extend([self.expand_all_replies])
        comment_list = await self.agent.page_interactor.scroll_load_selector(selector=comment_card_sel, threshold=n_target, scroll_step=500, same_th=20, load_wait=400, scroll_step_callbacks=callbacks)

        if n_target is not None:
            comment_list = comment_list[:n_target]

        return comment_list

    async def _parse_meta_info(self) -> dict:
        """
        Read meta info from the video detail page. (This method should be called after the first few comments are loaded)

        :return: (dict) {'view_count': int, 'comment_count': int }
        """
        try:
            view_count_elem = await self.agent.page_interactor.get_element(selector=view_count_sel)
            view_count_str = (await view_count_elem.text_content()).strip()
            view_count = search_comma_sep_num(view_count_str)
        except:
            view_count = None
            self.agent.debug_tool.warn(f"Could not find view count for video {self.agent.page.url}")
        try:
            comment_elem = await self.agent.page_interactor.get_element(selector=comment_count_sel)
            comment_count_str = (await comment_elem.text_content()).strip()
            comment_count = search_comma_sep_num(comment_count_str)
        except:
            comment_count = None
            self.agent.debug_tool.warn(f"Could not find comment count for video {self.agent.page.url}")
        return {
            "view_count": view_count,
            "comment_count": comment_count,
        }

    async def expand_all_replies(self):
        """
        Expand all replies.

        The native javascript code generally:

        - get the last 10 `more_reply_btns` and `more_btns`
        - click on each of them
        """
        self.debug_tool.debug(f"Expanding all replies...")
        js_code = '''() => {
            let more_reply_btns = Array.from(document.querySelectorAll("#more-replies > yt-button-shape > button > yt-touch-feedback-shape > div[aria-hidden='true']")).slice(-20);
            let more_btns = Array.from(document.querySelectorAll("#button > ytd-button-renderer > yt-button-shape > button > yt-touch-feedback-shape > div")).slice(-20);

            console.log(`more_reply_btns.length: ${more_reply_btns.length}`);
            console.log(`more_btns.length: ${more_btns.length}`);

            for(const more_reply_btn of more_reply_btns) {
                more_reply_btn.click();
            }
            for(const more_btn of more_btns) {
                more_btn.click();
            }
        }'''
        await self.agent.page_interactor.page.evaluate(js_code)
        self.debug_tool.debug(f"Expanding all replies finished")


__all__ = ['VideoPageHandler']
