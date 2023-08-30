import pandas as pd
from typing import List

from youcreep.common.pojo import VideoComment
from youcreep.page_parser.page_parser import PageParser
from youcreep.browser_agent.url_parser import YoutubeUrlParser
from youcreep.common.selectors.common_sels import comment_card_sel


class VideoPageParser(PageParser):
    def parse_comments(self, use_pandas: bool = False) -> List[VideoComment]:
        """
        Parse all comments in the YouTube video Page.

        :param use_pandas: (bool) whether to return a pandas.DataFrame
        :return: (List[VideoComment]) the list of comments
        """
        assert self.file_path is not None and self.soup is not None, "Please load webpage first"
        self.debug_tool.info(f"[{self.__class__.__name__}] Parsing comments in {self.file_path}...")
        # 查找所有的 ytd-comment-renderer 标签
        comment_renderers = self.soup.find_all(comment_card_sel)
        comments = [parse_comment_card(comment_card) for comment_card in comment_renderers]
        self.debug_tool.info(f"[{self.__class__.__name__}] Parsed {len(comments)} comments")
        if use_pandas:
            self.debug_tool.info(f"[{self.__class__.__name__}] Converting comments to pandas.DataFrame...")
            comments = pd.DataFrame([comment.to_dict() for comment in comments])
        return comments


def parse_comment_card(comment_card) -> VideoComment:
    is_reply = 'ytd-comment-replies-renderer' in comment_card.get('class', [])

    author_wrapper = comment_card.select_one('#header-author')
    author_name = author_wrapper.select_one('#author-text span').text.strip()
    author_url = author_wrapper.select_one('#author-text')['href']

    pub_time_wrapper = author_wrapper.select_one('yt-formatted-string.published-time-text')
    time_tag = pub_time_wrapper.text.strip().replace("（修改过）", "")
    comment_url = pub_time_wrapper.select_one('a')['href']
    comment_url_parsed = YoutubeUrlParser.parse_url(comment_url)

    thumbnail_wrapper = comment_card.select_one('#author-thumbnail')
    try:
        author_thumbnail = thumbnail_wrapper.select_one("img#img")['src']
    except KeyError:
        author_thumbnail = None

    content_wrapper = comment_card.select_one('#comment-content')
    content_text = content_wrapper.select_one('#content-text').text

    action_wrapper = comment_card.select_one('ytd-comment-action-buttons-renderer')
    like_count = action_wrapper.select_one('#vote-count-left').text.strip()

    return VideoComment.from_dict({
        'is_reply': is_reply,
        'author_name': author_name,
        'author_url': author_url,
        'publish_time': time_tag,
        'comment_id': comment_url_parsed["comment_id"],
        'parent_comment_id': comment_url_parsed["parent_comment_id"],
        'video_id': comment_url_parsed["video_id"],
        'author_thumbnail': author_thumbnail,
        'content_text': content_text,
        'like_count': like_count
    })


__all__ = ['VideoPageParser']
