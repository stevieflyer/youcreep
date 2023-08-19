class VideoComment:
    """
    `VideoComment` is a POJO class that represents a comment on a video.

    This class is used to store the data of a comment on a video.
    VideoComment is crawled from a video page.
    """
    def __init__(self):
        self.is_reply: bool = None
        self.author_name: str = None
        self.author_url = None
        self.comment_id: str = None
        self.parent_comment_id = None
        self.publish_time = None
        self.video_id = None
        self.author_thumbnail: str = None
        self.content_text = None
        self.like_count = None

    def to_dict(self):
        return {
            "comment_id": self.comment_id,
            "is_reply": self.is_reply,
            "author_name": self.author_name,
            "author_url": self.author_url,
            "publish_time": self.publish_time,
            "parent_comment_id": self.parent_comment_id,
            "video_id": self.video_id,
            "author_thumbnail": self.author_thumbnail,
            "content_text": self.content_text,
            "like_count": self.like_count
        }

    @classmethod
    def from_dict(cls, data_dict: dict):
        comment = cls()
        for key, value in data_dict.items():
            if hasattr(comment, key):
                setattr(comment, key, value)
        assert comment.comment_id is not None, "Comment ID cannot be None."
        return comment

    def __str__(self):
        return f"{self.__class__.__name__}(comment_id={self.comment_id})"

    def __repr__(self):
        return self.__str__()


__all__ = ['VideoComment']
