from deprecated import deprecated
from pyppeteer.element_handle import ElementHandle

from .url_parser import YoutubeUrlParser
from youcreep.dao.pojo import VideoInfo
from ._base_page_parser import BaseParserHandler


class SearchResultPageParser(BaseParserHandler):
    """
    Parser Handler for retrieving video info from video card element.
    """

    # noinspection PyTypeChecker
    async def parse(self, video_card: ElementHandle) -> VideoInfo:
        data_dict = {}

        text_wrapper = await video_card.querySelector(".text-wrapper.style-scope.ytd-video-renderer")
        title_wrapper = await text_wrapper.querySelector("#title-wrapper")
        meta_wrapper = await text_wrapper.querySelector("#metadata-line")
        channel_wrapper = await text_wrapper.querySelector("#channel-info")

        # parse title
        video_title = await title_wrapper.querySelector('#video-title')
        title = await self.agent.data_extractor.get_text(video_title)
        title = title.strip()
        data_dict["title"] = title

        video_href: str = await (await video_title.getProperty('href')).jsonValue()
        video_href = video_href.strip().split("&pp=")[0]
        video_href_info: dict = YoutubeUrlParser.parse_url(video_href)
        data_dict["video_id"] = video_href_info["video_id"]
        data_dict["is_short"] = video_href_info["type"] == "short"
        data_dict["video_url"] = video_href

        # parse meta
        meta_span_list = await meta_wrapper.querySelectorAll('span')
        view_count = await self.agent.data_extractor.get_text(meta_span_list[0])
        data_dict["view_count"] = view_count
        try:
            publish_time = await self.agent.data_extractor.get_text(meta_span_list[1])
            data_dict["publish_time"] = publish_time
        except IndexError:
            self.agent.debug_tool.warn(f"Could not find publish time for video {data_dict['video_id']}, url: {video_href}")

        # parse channel
        channel_thumbnail = await channel_wrapper.querySelector('#channel-thumbnail')
        channel_text = await self.agent.data_extractor.get_text(channel_wrapper)
        channel_name = channel_text.strip().split('\n')[0]
        channel_href = await (await channel_thumbnail.getProperty('href')).jsonValue()
        data_dict["channel_name"] = channel_name
        data_dict["channel_url"] = channel_href

        # desc info
        text_list = await text_wrapper.querySelectorAll("yt-formatted-string.style-scope.ytd-video-renderer")
        desc_text = await self.agent.data_extractor.get_text(text_list[-1])
        data_dict["desc_text"] = desc_text

        return VideoInfo.from_dict(data_dict)

    @deprecated(reason="This method is deprecated, now the is_short info is inferred by YoutubeUrlParser.")
    async def _is_short_video(self, video_card: ElementHandle) -> bool:
        """
        Check if the video is a short video.

        :param video_card: (ElementHandle) the video card element
        :return: (bool) True if the video is a short video, False otherwise
        """
        thumbnail = await video_card.querySelector("#thumbnail")
        text = await self.agent.data_extractor.get_text(thumbnail)
        text = text.strip()
        return 'SHORTS' in text


__all__ = ["SearchResultPageParser"]
