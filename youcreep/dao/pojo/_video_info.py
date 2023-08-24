class VideoInfo:
    """
    VideoInfo is a class that contains information about a video.

    This class is used to store the information of a video.
    VideoInfo is crawled from a video card from a search result page.
    """
    def __init__(self):
        self.video_id: str = None
        self.title: str = None
        self.video_url = None
        self.is_short: bool = None
        self.view_count = None
        self.publish_time = None
        self.channel_name: str = None
        self.channel_url = None
        self.desc_text: str = None
        self.comment_count: str = None

    def to_dict(self):
        return {
            "video_id": self.video_id,
            "title": self.title,
            "video_url": self.video_url,
            "is_short": self.is_short,
            "view_count": self.view_count,
            "publish_time": self.publish_time,
            "channel_name": self.channel_name,
            "channel_url": self.channel_url,
            "desc_text": self.desc_text,
            "comment_count": self.comment_count,
        }

    @classmethod
    def from_dict(cls, data_dict: dict):
        video = cls()
        for key, value in data_dict.items():
            if hasattr(video, key):
                setattr(video, key, value)
        assert video.video_id is not None, "Video ID cannot be None."
        return video

    def __str__(self):
        return f"VideoInfo(video_id={self.video_id})"

    def __repr__(self):
        return self.__str__()


__all__ = ['VideoInfo']
