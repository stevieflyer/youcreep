import enum


class FilterSection(enum.Enum):
    PUBLISH_DATE = 0
    TYPE = 1
    LENGTH = 2
    FUNCTION = 3
    ORDER_BY = 4


class FilterPublishDateOption(enum.Enum):
    LAST_HOUR = 0
    TODAY = 1
    THIS_WEEK = 2
    THIS_MONTH = 3
    THIS_YEAR = 4


class FilterTypeOption(enum.Enum):
    VIDEO = 0
    CHANNEL = 1
    PLAYLIST = 2
    MOVIE = 3


class FilterLengthOption(enum.Enum):
    SHORT = 0
    MEDIUM = 1
    LONG = 2


class FilterFunctionOption(enum.Enum):
    LIVE = 0
    _4K = 1
    HD = 2
    SUBTITLES = 3
    CREATIVE_COMMONS = 4
    _360 = 5
    VR180 = 6
    _3D = 7
    HDR = 8
    LOCATION = 9
    PURCHASES = 10


class FilterOrderByOption(enum.Enum):
    RELEVANCE = 0
    UPLOAD_DATE = 1
    VIEW_COUNT = 2
    RATING = 3
