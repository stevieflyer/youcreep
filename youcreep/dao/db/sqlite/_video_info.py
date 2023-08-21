from typing import Dict

from cetino.db.sqlite.type import SQLiteDataType
from cetino.db.sqlite.table_storage import SQLiteTableStorage


class VideoInfoTableStorage(SQLiteTableStorage):

    primary_key_tuple = ("video_id",)

    @property
    def fields(self) -> Dict[str, SQLiteDataType]:
        return {
            "video_id": SQLiteDataType.TEXT,
            "title": SQLiteDataType.TEXT,
            "video_url": SQLiteDataType.TEXT,
            "is_short": SQLiteDataType.INTEGER,
            "view_count": SQLiteDataType.TEXT,
            "publish_time": SQLiteDataType.TEXT,
            "channel_name": SQLiteDataType.TEXT,
            "channel_url": SQLiteDataType.TEXT,
            "desc_text": SQLiteDataType.TEXT
        }

    @property
    def table_name(self) -> str:
        return "video_info"
