from typing import Dict

from cetino.db.sqlite.type import SQLiteDataType
from cetino.db.sqlite.table_storage import SQLiteTableStorage


class VideoCommentTableStorage(SQLiteTableStorage):

    primary_key_tuple = ("comment_id",)

    @property
    def fields(self) -> Dict[str, SQLiteDataType]:
        return {
            "comment_id": SQLiteDataType.TEXT,
            "is_reply": SQLiteDataType.INTEGER,
            "author_name": SQLiteDataType.TEXT,
            "author_url": SQLiteDataType.TEXT,
            "publish_time": SQLiteDataType.TEXT,
            "parent_comment_id": SQLiteDataType.TEXT,
            "video_id": SQLiteDataType.TEXT,
            "author_thumbnail": SQLiteDataType.TEXT,
            "content_text": SQLiteDataType.TEXT,
            "like_count": SQLiteDataType.TEXT
        }

    @property
    def table_name(self) -> str:
        return "video_comment"
