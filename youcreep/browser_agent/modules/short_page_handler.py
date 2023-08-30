import asyncio

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
        await self.agent.page.click(selector=comment_btn_sel)
        self.debug_tool.info(f"Opening comment panel successfully")

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
        comment_count = await (await self.agent.page.query_selector(comment_count_sel)).text_content()
        like_count = await (await self.agent.page.query_selector(like_count_sel)).text_content()

        return {
            'comment_count': comment_count,
            'like_count': like_count,
        }

    async def load_all_comments(self):
        # Step 1: 打开评论面板
        await self.open_comment_panel()
        meta_info = await self.parse_meta_info()
        comment_count = int(meta_info['comment_count'])
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
            if len(comments) >= comment_count or same_count >= same_th:
                self.debug_tool.info(f"Loaded all comments, total {len(comments)} comments, target: {comment_count}, same_count: {same_count}, same_th: {same_th}")
                break
            n_comments = len(comments)
            if n_comments > 0:
                last_comment = comments[-1]
                self.debug_tool.info(f"Scrolling to last comment...")
                await last_comment.scroll_into_view_if_needed()
        return comments


__all__ = ['ShortPageHandler']
