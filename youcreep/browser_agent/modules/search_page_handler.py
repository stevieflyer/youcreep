import asyncio
import enum
import playwright.async_api
from typing import List, Callable

from youcreep.browser_agent.url_parser import YouTubeUrlType
from youcreep.browser_agent.modules.page_handler import PageHandler
from youcreep.common.selectors.common_sels import video_card_sel
from youcreep.common.selectors.search_result_page import filter_toggle_sel, filter_section_sel, filter_option_sel


class FilterSection(enum.Enum):
    PUBLISH_DATE = 0
    TYPE = 1
    LENGTH = 2
    FUNCTION = 3
    ORDER_BY = 4


class FilterPublishDateOption(enum.Enum):
    LAST_HOUR = 0
    TODAY = 1
    THIS_WEEK = 2
    THIS_MONTH = 3
    THIS_YEAR = 4


class FilterTypeOption(enum.Enum):
    VIDEO = 0
    CHANNEL = 1
    PLAYLIST = 2
    MOVIE = 3


class FilterLengthOption(enum.Enum):
    SHORT = 0
    MEDIUM = 1
    LONG = 2


class FilterFunctionOption(enum.Enum):
    LIVE = 0
    _4K = 1
    HD = 2
    SUBTITLES = 3
    CREATIVE_COMMONS = 4
    _360 = 5
    VR180 = 6
    _3D = 7
    HDR = 8
    LOCATION = 9
    PURCHASES = 10


class FilterOrderByOption(enum.Enum):
    RELEVANCE = 0
    UPLOAD_DATE = 1
    VIEW_COUNT = 2
    RATING = 3


SECTION_OPTION_DICT = {
    FilterSection.PUBLISH_DATE: FilterPublishDateOption,
    FilterSection.TYPE: FilterTypeOption,
    FilterSection.LENGTH: FilterLengthOption,
    FilterSection.FUNCTION: FilterFunctionOption,
    FilterSection.ORDER_BY: FilterOrderByOption
}


class SearchPageHandler(PageHandler):
    page_type = YouTubeUrlType.SEARCH

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
        await self.agent.page_interactor.click(selector=filter_toggle_sel)

        # 2. 选择 filter
        filter_group_list = await self.agent.page_interactor.get_elements(filter_section_sel)
        filter_group = filter_group_list[filter_section.value]
        filter_group_name_elem = await filter_group.query_selector(selector="#filter-group-name")
        filter_title = (await filter_group_name_elem.text_content()).strip()
        filter_option_elem_list = await filter_group.query_selector_all(selector=filter_option_sel)
        filter_option_elem = await filter_option_elem_list[filter_option.value].query_selector("a")
        option_text = (await filter_option_elem.text_content()).strip()

        # 3. 点击 filter
        self.debug_tool.logger.info(f"Filtering searching result, filter_section_title: {filter_title}, option: {option_text}")
        await filter_option_elem.click()

        # 4. 等待一小会
        await asyncio.sleep(0.5)

    async def scroll_load_video_cards(self, n_target: int, callbacks: List[Callable] = None) -> List[playwright.async_api.ElementHandle]:
        """
        Scroll down to load more video cards.

        @in_page: search result page

        @out_page: search result page

        :param n_target: (int) The target number of video cards to load.
        :param callbacks: (List[Callable]) The callback function to call after each scroll step.
        :return: (List[ElementHandle]) The list of video card elements.
        """
        video_list = await self.agent.page_interactor.scroll_load_selector(selector=video_card_sel, threshold=n_target, scroll_step=1000, same_th=30, load_wait=400, scroll_step_callbacks=callbacks)

        if n_target is not None:
            video_list = video_list[:n_target]

        return video_list
