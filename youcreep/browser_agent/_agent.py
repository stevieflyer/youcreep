import asyncio
from typing import List, Callable

import pyppeteer.element_handle
from zephyrion.pypp import PyppeteerAgent

from youcreep.config.filter_enum import FilterSection
from youcreep.page_parser.selectors.common import search_input_sel, clear_input_btn_selector, search_submit_sel, \
    dismiss_premium_btn, comment_card_sel, video_card_sel
from youcreep.page_parser.selectors.video_page import subtitle_btn_sel
from youcreep.page_parser.selectors.search_result_page import filter_toggle_sel, filter_section_sel, filter_option_sel
from youcreep.page_parser.modules.url_parser import YoutubeUrlParser


class YoutubeBrowserAgent(PyppeteerAgent):
    """
    The browser agent for YouTube.

    `YoutubeBrowserAgent` can monitor all kinds of interactions with YouTube.
    Such as:

    - Search videos and filter the search result.
    - Open a video and scroll down to load all comments.
    """
    home_page = "https://www.youtube.com/"
    url_parser = YoutubeUrlParser()

    async def start(self) -> None:
        """
        Start the browser manager and go to the home page(*YouTube.com*).

        :return: (None)
        """
        await super().start()
        await self.browser_manager.go(self.home_page)
        # set viewport
        await self.page_interactor.set_viewport(width=1920, height=1080)

    async def stop(self) -> None:
        """
        Stop the browser manager.

        :return: (None)
        """
        await super().stop()

    async def search(self, search_term: str) -> None:
        """
        Search videos by `search_term`.

        @in_page: any YouTube page

        @out_page: search result page

        :param search_term:  (str) The search term.
        :return: (None)
        """
        # 1. Type input the search term
        await self._type_input_search_term(search_term=search_term)

        # 2. Click the search submit button until the search result page is loaded.
        is_search_page = False
        n_retry, max_retry = 0, 5
        while not is_search_page:
            await self.page_interactor.click(selector=search_submit_sel, new_page=True)
            current_url: str = await self.browser_manager.get_url()
            is_search_page = self.url_parser.is_search_url(current_url)
            n_retry += 1
        if is_search_page is False:
            raise RuntimeError(f"Failed to search for {search_term} after {max_retry} retries.")
        else:
            self.debug_tool.info(f"Search for {search_term} successfully after {n_retry} retries.")

    async def go_video_page(self, video_url: str, initial_scroll: int = 5) -> None:
        """
        Go to the video page.

        @in_page: any YouTube page

        @out_page: video page

        :param video_url: (str) The URL of the video.
        :param initial_scroll: (int) The number of times to scroll to the bottom of the page for loading the page.
        :return: (None)
        """
        self.debug_tool.info(f"Going to the video page: {video_url}")
        if not (YoutubeUrlParser.is_video_url(video_url) or YoutubeUrlParser.is_short_url(video_url)):
            raise ValueError(f"The url {video_url} is not a valid video url.")
        await self.browser_manager.go(video_url)
        for i in range(initial_scroll):
            if i % 4 == 0:
                self.debug_tool.info(f"Scrolling to the bottom of the page for {i + 1} time(s) for loading the page...")
            await self.page_interactor.scroll_by(x_disp=0, y_disp=2000)
            await asyncio.sleep(0.4)
        await self.dismiss_premium_modal()

    async def _type_input_search_term(self, search_term: str) -> None:
        """
        Type input the search term.

        :param search_term: (str) The search term.
        :return: (None)
        """
        # 1. clear the input
        try:
            await self.page_interactor.click(selector=clear_input_btn_selector)
        except Exception:
            pass

        # 2. type the input
        await self.page_interactor.type_input(selector=search_input_sel, text=search_term)

    async def filter_search_result(self, filter_section: FilterSection, filter_option) -> None:
        """
        Filter the search result.

        @in_page: search result page

        @out_page: search result page

        :param filter_section: (int) The filter section.
        :param filter_option:  (int) The index of the filter option.
        :return: (None)
        """
        # 1. 打开 filter modal
        await self.page_interactor.click(selector=filter_toggle_sel)

        # 2. 选择 filter
        filter_group_list = await self.page_interactor.get_elements(filter_section_sel)
        filter_group = filter_group_list[filter_section.value]
        filter_group_name_elem = await filter_group.querySelector("#filter-group-name")
        filter_title = (await self.data_extractor.get_text(filter_group_name_elem)).strip()
        filter_option_elem_list = await filter_group.querySelectorAll(filter_option_sel)
        filter_option_elem = await filter_option_elem_list[filter_option.value].querySelector("a")
        option_text = (await self.data_extractor.get_text(filter_option_elem)).strip()

        # 3. 点击 filter
        self.debug_tool.logger.debug(
            f"Filtering searching result, filter_section_title: {filter_title}, option: {option_text}")
        await filter_option_elem.click()

    async def scroll_load_video_cards(self, n_target: int, callbacks: List[Callable] = None) -> List[pyppeteer.element_handle.ElementHandle]:
        """
        Scroll down to load more video cards.

        @in_page: search result page

        @out_page: search result page

        :param n_target: (int) The target number of video cards to load.
        :param callbacks: (List[Callable]) The callback function to call after each scroll step.
        :return: (List[ElementHandle]) The list of video card elements.
        """
        video_list = await self.page_interactor.scroll_load_selector(selector=video_card_sel, threshold=n_target,
                                                                     scroll_step=800, same_th=50,
                                                                     scroll_step_callbacks=callbacks)

        if n_target is not None:
            video_list = video_list[:n_target]

        return video_list

    async def scroll_load_comments(self, n_target: int, callbacks: List[Callable] = None) -> List[pyppeteer.element_handle.ElementHandle]:
        """
        Scroll down to load more comments.

        @in_page: video page

        @out_page: video page

        :param n_target: (int) The target number of comments to load.
        :param callbacks: (List[Callable]) The callback function to call after each scroll step.
        :return: (int) The number of comments loaded.
        """
        default_callbacks = [self.expand_all_replies]
        if callbacks is not None:
            default_callbacks.extend(callbacks)

        comment_list = await self.page_interactor.scroll_load_selector(selector=comment_card_sel, threshold=n_target,
                                                                       scroll_step=800, same_th=50,
                                                                       scroll_step_callbacks=default_callbacks)

        if n_target is not None:
            comment_list = comment_list[:n_target]

        return comment_list

    async def toggle_subtitle(self):
        """
        Toggle the subtitle.

        But now it's not working since the pyppeteer chromium is too old to support the YouTube subtitle function
        """
        subtitle_btn = await self.page_interactor.get_element(selector=subtitle_btn_sel)
        await self.click(selector=subtitle_btn_sel)
        btn_title = await self.get_attr(subtitle_btn, "title")
        if btn_title is not None and ("无法" in btn_title or '無法' in btn_title or "cannot" in btn_title):
            self.debug_tool.warn(f"Failed to toggle subtitle, btn_title: {btn_title}, current url: {self.url}")
            return False
        else:
            return True

    async def expand_all_replies(self):
        """
        Expand all replies.

        The native javascript code generally:

        - get the last 10 `more_reply_btns` and `more_btns`
        - click on each of them
        """
        js_code = '''() => {
            let more_reply_btns = Array.from(document.querySelectorAll("#more-replies > yt-button-shape > button > yt-touch-feedback-shape > div[aria-hidden='true']")).slice(-10);
            let more_btns = Array.from(document.querySelectorAll("#button > ytd-button-renderer > yt-button-shape > button > yt-touch-feedback-shape > div")).slice(-10);

            console.log(`more_reply_btns.length: ${more_reply_btns.length}`);
            console.log(`more_btns.length: ${more_btns.length}`);

            for(const more_reply_btn of more_reply_btns) {
                more_reply_btn.click();
            }
            for(const more_btn of more_btns) {
                more_btn.click();
            }
        }'''
        await self.page_interactor._page.evaluate(js_code)

    async def dismiss_premium_modal(self):
        """
        Dismiss the premium modal.

        :return:
        """
        try:
            btn = await self.page_interactor.get_element(selector=dismiss_premium_btn)

            await btn.click()
        except Exception:
            self.debug_tool.warn(f"Failed to dismiss premium modal.(sel: {dismiss_premium_btn})")


__all__ = ["YoutubeBrowserAgent"]
