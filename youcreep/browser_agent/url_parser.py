import re
import enum


class YouTubeUrlType(enum.Enum):
    VIDEO = "video"
    SHORT = "short"
    SEARCH = "search"
    USER = "user"
    COMMENT = "comment"
    REPLY_COMMENT = "reply_comment"
    UNKNOWN = "unknown"


class YoutubeUrlParser:
    """
    YouTube url parser.
    """
    video_url_regexp = r"(https://www\.youtube\.com)?/watch\?v=(?P<video_id>[^&]+)$"
    short_url_regexp = r"(https://www\.youtube\.com)?/shorts/(?P<video_id>[^/]+)"
    search_url_regexp = r"(https://www\.youtube\.com)?/results\?search_query=(?P<search_term>[^&]+)"
    user_url_regexp = r"(https://www\.youtube\.com)?/@(?P<user_id>[^/]+)"
    comment_url_regexp = r"(https://www\.youtube\.com)?/watch\?v=(?P<video_id>[^&]+)&lc=(?P<comment_id>[^&\.]+)"

    @staticmethod
    def parse_url(url: str) -> dict:
        """
        Parse the url and return the result.

        :param url: (str) the url to be parsed
        :return: (dict) {'type': YouTubeUrlType, **other_args }
        """
        if re.match(YoutubeUrlParser.comment_url_regexp, url):
            match = re.match(YoutubeUrlParser.comment_url_regexp, url)
            video_id = match.group("video_id")
            comment_id = url.split("&lc=")[-1]
            if "." in comment_id:
                ids = comment_id.split(".")
                comment_id = ids[1]
                parent_comment_id = ids[0]
                comment_type = YouTubeUrlType.REPLY_COMMENT
            else:
                parent_comment_id = None
                comment_type = YouTubeUrlType.COMMENT
            return {"type": comment_type, "video_id": video_id, "comment_id": comment_id,
                    "parent_comment_id": parent_comment_id}

        if re.match(YoutubeUrlParser.video_url_regexp, url):
            match = re.match(YoutubeUrlParser.video_url_regexp, url)
            video_id = match.group("video_id")
            return {"type": YouTubeUrlType.VIDEO, "video_id": video_id}

        if re.match(YoutubeUrlParser.short_url_regexp, url):
            match = re.match(YoutubeUrlParser.short_url_regexp, url)
            video_id = match.group("video_id")
            return {"type": YouTubeUrlType.SHORT, "video_id": video_id}

        if re.match(YoutubeUrlParser.search_url_regexp, url):
            match = re.match(YoutubeUrlParser.search_url_regexp, url)
            search_term = match.group("search_term")
            return {"type": YouTubeUrlType.SEARCH, "search_term": search_term}

        if re.match(YoutubeUrlParser.user_url_regexp, url):
            match = re.match(YoutubeUrlParser.user_url_regexp, url)
            user_id = match.group("user_id")
            return {"type": YouTubeUrlType.USER, "user_id": user_id}

        return {"type": YouTubeUrlType.UNKNOWN}

    @staticmethod
    def is_video_url(url) -> bool:
        return YoutubeUrlParser.parse_url(url)["type"] == YouTubeUrlType.VIDEO

    @staticmethod
    def is_short_url(url) -> bool:
        return YoutubeUrlParser.parse_url(url)["type"] == YouTubeUrlType.SHORT

    @staticmethod
    def is_search_url(url) -> bool:
        return YoutubeUrlParser.parse_url(url)["type"] == YouTubeUrlType.SEARCH

    @staticmethod
    def is_user_url(url) -> bool:
        return YoutubeUrlParser.parse_url(url)["type"] == YouTubeUrlType.USER

    @staticmethod
    def is_comment_url(url) -> bool:
        url_type = YoutubeUrlParser.parse_url(url)["type"]
        return url_type == YouTubeUrlType.COMMENT or url_type == YouTubeUrlType.REPLY_COMMENT

    @staticmethod
    def is_reply_comment_url(url) -> bool:
        return YoutubeUrlParser.parse_url(url)["type"] == YouTubeUrlType.REPLY_COMMENT


__all__ = ['YoutubeUrlParser', "YouTubeUrlType"]
