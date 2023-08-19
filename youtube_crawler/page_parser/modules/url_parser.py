import re


class YoutubeUrlParser:
    video_url_regexp = r"(https://www\.youtube\.com)?/watch\?v=(?P<video_id>[^&]+)$"
    short_url_regexp = r"(https://www\.youtube\.com)?/shorts/(?P<video_id>[^/]+)"
    search_url_regexp = r"(https://www\.youtube\.com)?/results\?search_query=(?P<search_term>[^&]+)"
    user_url_regexp = r"(https://www\.youtube\.com)?/@(?P<user_id>[^/]+)"
    comment_url_regexp = r"(https://www\.youtube\.com)?/watch\?v=(?P<video_id>[^&]+)&lc=(?P<comment_id>[^&\.]+)"

    @staticmethod
    def parse_url(url):
        if re.match(YoutubeUrlParser.comment_url_regexp, url):
            match = re.match(YoutubeUrlParser.comment_url_regexp, url)
            video_id = match.group("video_id")
            comment_id = url.split("&lc=")[-1]
            if "." in comment_id:
                ids = comment_id.split(".")
                comment_id = ids[1]
                parent_comment_id = ids[0]
                comment_type = "reply_comment"
            else:
                parent_comment_id = None
                comment_type = "comment"
            return {"type": comment_type, "video_id": video_id, "comment_id": comment_id,
                    "parent_comment_id": parent_comment_id}

        if re.match(YoutubeUrlParser.video_url_regexp, url):
            match = re.match(YoutubeUrlParser.video_url_regexp, url)
            video_id = match.group("video_id")
            return {"type": "video", "video_id": video_id}

        if re.match(YoutubeUrlParser.short_url_regexp, url):
            match = re.match(YoutubeUrlParser.short_url_regexp, url)
            video_id = match.group("video_id")
            return {"type": "short", "video_id": video_id}

        if re.match(YoutubeUrlParser.search_url_regexp, url):
            match = re.match(YoutubeUrlParser.search_url_regexp, url)
            search_term = match.group("search_term")
            return {"type": "search", "search_term": search_term}

        if re.match(YoutubeUrlParser.user_url_regexp, url):
            match = re.match(YoutubeUrlParser.user_url_regexp, url)
            user_id = match.group("user_id")
            return {"type": "user", "user_id": user_id}

        return {"type": "unknown"}

    @staticmethod
    def is_video_url(url):
        return YoutubeUrlParser.parse_url(url)["type"] == "video"

    @staticmethod
    def is_short_url(url):
        return YoutubeUrlParser.parse_url(url)["type"] == "short"

    @staticmethod
    def is_search_url(url):
        return YoutubeUrlParser.parse_url(url)["type"] == "search"

    @staticmethod
    def is_user_url(url):
        return YoutubeUrlParser.parse_url(url)["type"] == "user"

    @staticmethod
    def is_comment_url(url):
        url_type = YoutubeUrlParser.parse_url(url)["type"]
        return url_type == "comment" or url_type == "reply_comment"

    @staticmethod
    def is_reply_comment_url(url):
        return YoutubeUrlParser.parse_url(url)["type"] == "reply_comment"


__all__ = ['YoutubeUrlParser']
