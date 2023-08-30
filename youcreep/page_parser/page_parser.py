import abc
import pathlib

from bs4 import BeautifulSoup
from gembox.debug_utils import Debugger
from gembox.io import ensure_pathlib_path

from youcreep.common.pojo import VideoComment
from .exception import FailedToLoadWebpageException
from youcreep.browser_agent.url_parser import YoutubeUrlParser


class PageParser(abc.ABC):
    """
    The base class of all page parsers, built upon BeautifulSoup.

    Page Parser is responsible for reading webpages from local files, and parsing the webpages to get the information.

    After `load_webpage`, you can always access the `soup` property to get the BeautifulSoup object.
    """
    def __init__(self, debug_tool: Debugger = None, encoding="utf-8"):
        self._encoding = encoding
        self._debug_tool = debug_tool if debug_tool is not None else Debugger()
        self._file_path = None
        self._soup = None

    def load_webpage(self, file_path: (str, pathlib.Path)):
        """
        Load webpage from local file.

        :param file_path: (str, pathlib.Path) the path to the local file
        :return: (None)
        """
        self.debug_tool.info(f"[{self.__class__.__name__}] Loading webpage from {file_path}...")
        try:
            self._file_path = ensure_pathlib_path(file_path)
            self._soup = self._read_webpage_from_file(file_path=file_path)
            self.debug_tool.info(f"[{self.__class__.__name__}] Loaded webpage from {file_path} successfully")
        except Exception:
            self._soup = None
            self._file_path = None
            self.debug_tool.error(f"[{self.__class__.__name__}] Failed to load webpage from {file_path}")
            raise FailedToLoadWebpageException(f"Failed to load webpage from {file_path}")

    def _read_webpage_from_file(self, file_path: (str, pathlib.Path)) -> BeautifulSoup:
        self.debug_tool.info(f"[{self.__class__.__name__}] Reading webpage from {file_path}...")
        with open(file_path, "r", encoding=self._encoding) as file:
            content = file.read()
        self.debug_tool.info(f"[{self.__class__.__name__}] Transforming {file_path} to BeautifulSoup...")
        return BeautifulSoup(content, 'lxml')

    @property
    def debug_tool(self) -> Debugger:
        return self._debug_tool

    @property
    def encoding(self) -> str:
        return self._encoding

    @property
    def file_path(self) -> pathlib.Path:
        return self._file_path

    @property
    def soup(self) -> BeautifulSoup:
        return self._soup


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
