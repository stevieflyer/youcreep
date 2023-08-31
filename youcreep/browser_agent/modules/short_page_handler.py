import asyncio

from gembox.re_utils import search_float_num

from youcreep.browser_agent.url_parser import YouTubeUrlType
from youcreep.browser_agent.modules.page_handler import PageHandler
from youcreep.common.selectors.short_page_sels import comment_btn_sel, more_reply_btn_sel, comment_count_sel, like_count_sel, comment_sel


class ShortPageHandler(PageHandler):
    page_type = YouTubeUrlType.SHORT

    async def go_short_page(self, url: str):
        """
        Go to a short page, and initialize the page.

        :param url: (str) the url of the short page
        :return: (None)
        """
        assert self.check_url(test_url=url) is True

        self.debug_tool.info(f"Going to short page {url}...")
        await self.agent.browser_mgr.go(url)

        # Initialization at a short page
        self.debug_tool.info(f"Waiting for comment button to appear...")
        await self.agent.page.wait_for_selector(comment_btn_sel)
        self.debug_tool.info(f"Go to short page {url} successfully")

    async def open_comment_panel(self):
        """
        Open the comment panel on the sideline of short video.

        :return: (None)
        """
        assert self.check_url() is True

        self.debug_tool.info(f"Opening comment panel...")
        if await self.agent.page.is_enabled(comment_btn_sel):
            await self.agent.page.click(selector=comment_btn_sel)
            self.debug_tool.info(f"Opening comment panel successfully")
            return True
        else:
            self.debug_tool.warn(f"Cannot open comment panel, because the comment button is disabled.")
            return False

    async def show_more_replies(self):
        """
        Click the last 20 show_more_reply buttons to load more replies.

        :return: (None)
        """
        btns = await self.agent.page.query_selector_all(more_reply_btn_sel)
        self.debug_tool.info(f"Found {len(btns)} show_more_reply_btn...")
        for i, btn in enumerate(btns[-20:]):
            if await btn.is_visible():
                await btn.click()

    async def parse_meta_info(self):
        """
        Parse the meta info of the current page.

        :return: (dict) {'comment_count': str, 'like_count': str }
        """
        comment_count_str = await (await self.agent.page.query_selector(comment_count_sel)).text_content()
        like_count_str = await (await self.agent.page.query_selector(like_count_sel)).text_content()

        try:
            comment_count = search_float_num(comment_count_str)
            if '万' in comment_count_str or '萬' in comment_count_str:
                comment_count *= 10000
            comment_count = int(comment_count)
        except:
            self.debug_tool.warn(f"Cannot parse comment_count: {comment_count_str}, set to 0")
            comment_count = 0
        try:
            like_count = search_float_num(like_count_str)
            if '万' in like_count_str or '萬' in like_count_str:
                like_count *= 10000
            like_count = int(like_count)
        except:
            self.debug_tool.warn(f"Cannot parse like_count: {like_count_str}, set to 0")
            like_count = 0

        self.debug_tool.info(f"parse_meta_info: comment_count: {comment_count}, like_count: {like_count}")

        return {
            'comment_count': comment_count,
            'like_count': like_count,
        }

    async def scroll_load_comment_cards(self, n_target: int = None):
        # Step 1: 打开评论面板
        if not await self.open_comment_panel():
            self.debug_tool.info(f"Comment panel is disabled, skip loading comments.")
            return []
        meta_info = await self.parse_meta_info()
        comment_count = int(meta_info['comment_count'])
        if n_target is None:
            n_target = comment_count
        else:
            n_target = min(n_target, comment_count)
        if n_target == 0:
            self.debug_tool.info(f"No comment is found, skip loading comments.")
            return []

        await self.agent.page.wait_for_selector(comment_sel)
        await asyncio.sleep(1.5)

        # Step 2: 点击加载更多按钮
        n_comments, comments = 0, []
        same_count, same_th = 0, 5
        while True:
            self.debug_tool.info(f"Clicking all show_more_reply_btn...")
            await asyncio.sleep(0.5)
            await self.show_more_replies()
            comments = await self.agent.page.query_selector_all(comment_sel)
            self.debug_tool.info(f"Loaded {len(comments)} comments, previous value: {n_comments}, same_count: {same_count}, same_th: {same_th}")
            if len(comments) == n_comments:
                same_count += 1
            if len(comments) > n_target or same_count >= same_th:
                self.debug_tool.info(f"Loaded enough comments, total {len(comments)} comments, target: {n_target}, same_count: {same_count}, same_th: {same_th}")
                break
            n_comments = len(comments)
            if n_comments > 0:
                last_comment = comments[-1]
                self.debug_tool.info(f"Scrolling to last comment...")
                await last_comment.scroll_into_view_if_needed()
        return comments


__all__ = ['ShortPageHandler']
