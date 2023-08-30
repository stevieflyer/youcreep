import pandas as pd
from typing import List

from gembox.re_utils import search_comma_sep_num

from youcreep.common.pojo import VideoInfo
from youcreep.page_parser.page_parser import PageParser
from youcreep.common.selectors.search_result_page import video_card_sel
from youcreep.browser_agent.url_parser import YoutubeUrlParser, YouTubeUrlType


class SearchPageParser(PageParser):
    def parse_videos(self, use_pandas: bool = False) -> List[VideoInfo]:
        """
        Parse all videos' info in the YouTube search Page.

        :param use_pandas: (bool) whether to return a pandas.DataFrame
        :return: (List[VideoInfo]) the list of videos
        """
        assert self.file_path is not None and self.soup is not None, "Please load webpage first"
        self.debug_tool.info(f"[{self.__class__.__name__}] Parsing videos in {self.file_path}...")
        video_cards = self.soup.find_all(video_card_sel)
        videos = [parse_video_card(video_card) for video_card in video_cards]
        self.debug_tool.info(f"[{self.__class__.__name__}] Parsed {len(videos)} videos")
        if use_pandas:
            self.debug_tool.info(f"[{self.__class__.__name__}] Converting comments to pandas.DataFrame...")
            videos = pd.DataFrame([comment.to_dict() for comment in videos])
        return videos


def parse_video_card(video_card) -> VideoInfo:
    data_dict = {}

    text_wrapper = video_card.select_one(".text-wrapper.style-scope.ytd-video-renderer")
    title_wrapper = text_wrapper.select_one("#title-wrapper")
    channel_wrapper = text_wrapper.select_one("#channel-info")

    # 提取视频标题
    video_title_element = title_wrapper.select_one('a#video-title')
    video_title = video_title_element['title']
    data_dict['title'] = video_title

    # 提取视频链接
    video_link_element = title_wrapper.select_one('a#video-title')
    video_url = video_link_element['href'].split("&pp=")[0]
    data_dict['video_url'] = video_url

    url_parsed = YoutubeUrlParser.parse_url(data_dict['video_url'])
    data_dict['video_id'] = url_parsed["video_id"]
    data_dict['is_short'] = url_parsed["type"] == YouTubeUrlType.SHORT

    # 提取发布时间和观看次数
    aria_label = video_link_element['aria-label']
    # 解析aria-label以获取发布时间和观看次数
    if data_dict['is_short'] is True:
        aria_label = ("-".join(aria_label.split("-")[:-1])).strip()
    parts = aria_label.split(" ")
    publish_time = parts[-3]
    duration = parts[-2]
    view_count = search_comma_sep_num(parts[-1])
    data_dict['publish_time'] = publish_time
    data_dict['duration'] = duration
    data_dict['view_count'] = view_count

    # parse channel
    channel_text = channel_wrapper.text
    data_dict['channel_name'] = channel_text.strip().split('\n')[0]
    data_dict['channel_url'] = channel_wrapper.select_one('a')['href']

    # desc info
    text_list = text_wrapper.select("yt-formatted-string.style-scope.ytd-video-renderer")
    data_dict['desc_text'] = text_list[-1].text if text_list else ""

    return VideoInfo.from_dict(data_dict)


__all__ = ['SearchPageParser']
