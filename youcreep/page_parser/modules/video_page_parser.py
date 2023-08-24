import re
import pyppeteer.element_handle
from gembox.re_utils import search_comma_sep_num

from .url_parser import YoutubeUrlParser
from youcreep.dao.pojo import VideoComment
from ._base_page_parser import BaseParserHandler
from youcreep.page_parser.selectors.video_page import view_count_sel, comment_count_sel


class VideoPageParser(BaseParserHandler):
    """
    Parser Handler for retrieving video comment from video comment element.
    """
    async def parse_comment_card(self, comment_card: pyppeteer.element_handle.ElementHandle) -> VideoComment:
        """
        Parse comment info from comment card element listed in the video page.

        :param comment_card: (pyppeteer.element_handle.ElementHandle) comment card element
        :return: (VideoComment) comment info
        """
        data_dict = {}

        is_reply = await self._is_reply(comment_card)
        data_dict['is_reply'] = is_reply

        # 1. header(发布者信息)
        author_wrapper = await comment_card.querySelector('#header-author')
        # # author name
        author_text_wrapper = await author_wrapper.querySelector('#author-text')  # `a` element
        author_name = (await self.agent.data_extractor.get_text(await author_text_wrapper.querySelector('span'))).strip()
        author_url = await self.agent.data_extractor.get_attr(author_text_wrapper, 'href')
        data_dict['author_name'] = author_name
        data_dict['author_url'] = author_url
        # # publish time
        pub_time_wrapper = await author_wrapper.querySelector('yt-formatted-string.published-time-text')
        time_tag = (await self.agent.data_extractor.get_text(pub_time_wrapper)).strip("（修改过）")
        data_dict['publish_time'] = time_tag
        comment_url = (await self.agent.data_extractor.get_attr(await pub_time_wrapper.querySelector('a'), 'href')).strip()
        comment_url_parsed = YoutubeUrlParser.parse_url(comment_url)
        comment_id = comment_url_parsed['comment_id']
        parent_comment_id = comment_url_parsed['parent_comment_id']
        video_id = comment_url_parsed['video_id']
        data_dict['comment_id'] = comment_id
        data_dict['parent_comment_id'] = parent_comment_id
        data_dict['video_id'] = video_id
        # # thumbnail
        thumbnail_wrapper = await comment_card.querySelector('#author-thumbnail')
        author_thumbnail = await self.agent.data_extractor.get_attr(await thumbnail_wrapper.querySelector("img#img"), 'src')
        data_dict['author_thumbnail'] = author_thumbnail

        # 2. content wrapper(评论正文)
        content_wrapper = await comment_card.querySelector('#comment-content')
        content_text = await self.agent.data_extractor.get_text((await content_wrapper.querySelector('#content-text')))
        data_dict['content_text'] = content_text

        # 3. action wrapper(点赞转发)
        action_wrapper = await comment_card.querySelector('ytd-comment-action-buttons-renderer')
        like_count = (await self.agent.data_extractor.get_text(await action_wrapper.querySelector('#vote-count-left'))).strip()
        data_dict['like_count'] = like_count

        return VideoComment.from_dict(data_dict)

    async def parse_meta_info(self):
        """
        Read meta info from the video detail page. (This method should be called after the first few comments are loaded)

        :return: (dict) meta info
        """
        try:
            view_count_str = (await self.agent.get_texts(view_count_sel))[0].strip()
            view_count = search_comma_sep_num(view_count_str)
        except:
            view_count = None
            self.agent.debug_tool.warn(f"Could not find view count for video {self.agent.url}")
        try:
            comment_count_str = (await self.agent.get_texts(comment_count_sel))[0].strip()
            comment_count = search_comma_sep_num(comment_count_str)
        except:
            comment_count = None
            self.agent.debug_tool.warn(f"Could not find comment count for video {self.agent.url}")
        return {
            "view_count": view_count,
            "comment_count": comment_count,
        }

    async def parse_comment_card_test(self, comment_card: pyppeteer.element_handle.ElementHandle) -> VideoComment:
        """
        Parse comment info from comment card element listed in the video page.

        :param comment_card: (pyppeteer.element_handle.ElementHandle) comment card element
        :return: (VideoComment) comment info
        """

        script = """
        function(commentCard) {

            const isReply = commentCard.classList.contains('ytd-comment-replies-renderer');

            const authorWrapper = commentCard.querySelector('#header-author');
            const authorName = authorWrapper.querySelector('#author-text span').innerText.trim();
            const authorUrl = authorWrapper.querySelector('#author-text').href;

            const pubTimeWrapper = authorWrapper.querySelector('yt-formatted-string.published-time-text');
            const timeTag = pubTimeWrapper.innerText.trim().replace("（修改过）", "");
            const commentUrl = pubTimeWrapper.querySelector('a').href;

            const thumbnailWrapper = commentCard.querySelector('#author-thumbnail');
            const authorThumbnail = thumbnailWrapper.querySelector("img#img").src;

            const contentWrapper = commentCard.querySelector('#comment-content');
            const contentText = contentWrapper.querySelector('#content-text').innerText;

            const actionWrapper = commentCard.querySelector('ytd-comment-action-buttons-renderer');
            const likeCount = actionWrapper.querySelector('#vote-count-left').innerText.trim();

            return {
                isReply,
                authorName,
                authorUrl,
                timeTag,
                commentUrl,
                authorThumbnail,
                contentText,
                likeCount
            };
        }
        """

        data_dict = await self.agent.page_interactor._page.evaluate(script, comment_card)
        comment_url_parsed = YoutubeUrlParser.parse_url(data_dict['commentUrl'])

        return VideoComment.from_dict({
            'is_reply': data_dict['isReply'],
            'author_name': data_dict['authorName'],
            'author_url': data_dict['authorUrl'],
            'publish_time': data_dict['timeTag'],
            'comment_id': comment_url_parsed['comment_id'],
            'parent_comment_id': comment_url_parsed['parent_comment_id'],
            'video_id': comment_url_parsed['video_id'],
            'author_thumbnail': data_dict['authorThumbnail'],
            'content_text': data_dict['contentText'],
            'like_count': data_dict['likeCount']
        })

    async def _is_reply(self, comment_card: pyppeteer.element_handle.ElementHandle) -> bool:
        """
        Check if the comment is a reply to another comment.

        if comment has class ytd-comment-replies-renderer, then is_reply is True
        :param comment_card: (pyppeteer.element_handle.ElementHandle) comment card element
        :return: (bool) whether the comment is a reply to header comment
        """
        is_reply = await self.agent.data_extractor.has_cls(comment_card, 'ytd-comment-replies-renderer')
        return is_reply


__all__ = ["VideoPageParser"]
