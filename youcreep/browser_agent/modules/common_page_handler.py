import pathlib

from youcreep.common.selectors import common_sels
from youcreep.browser_agent.modules.page_handler import PageHandler


class CommonPageHandler(PageHandler):
    page_type = None

    async def search(self, search_term: str):
        """
        Search the search term in the search bar.

        @in-page: any YouTube page
        @out-page: search result page

        :param search_term: (str) the search term
        :return:
        """
        self.debug_tool.info(f"Searching {search_term}...")
        await self.type_search(text=search_term)
        self.debug_tool.info(f"Submit the search term...")
        await self.agent.page.click(selector=common_sels.search_submit_sel)
        self.debug_tool.info(f"Searching {search_term} successfully")

    async def type_search(self, text: str, clear_prev: bool = True):
        """
        Type text in the search bar.

        :param text: (str) the content to type in the search bar
        :param clear_prev: (bool) whether to clear the previous content in the search bar
        :return: (None)
        """
        self.debug_tool.info(f"Typing in search bar...(text: {text})")
        await self.agent.page.click(selector=common_sels.search_input_sel)
        if clear_prev and (await self.agent.page.is_visible(common_sels.clear_input_btn_selector)):
            await self.agent.page.click(common_sels.clear_input_btn_selector)
        await self.agent.page.type(selector=common_sels.search_input_sel, text=text)
        self.debug_tool.info(f"Typing in search bar successfully.")

    async def download_page(self, file_path: (str, pathlib.Path), encoding="utf-8"):
        """
        Download current web page. Save to the file system.

        :param file_path: (str, pathlib.Path) the file path to save the web page
        :param encoding: (str) the file encoding, default is 'utf-8'
        :return:
        """
        return await self.agent.page_interactor.download_html(file_path=file_path, encoding=encoding)


__all__ = ["CommonPageHandler"]
