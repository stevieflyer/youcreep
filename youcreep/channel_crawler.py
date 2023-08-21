from typing import Dict

from youcreep._base_crawler import YoutubeBaseCrawler


class YoutubeChannelCrawler(YoutubeBaseCrawler):
    """
    Crawler for channel infos on YouTube.
    """
    def crawl(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def required_fields(cls) -> Dict:
        pass

    @classmethod
    def optional_fields(cls) -> Dict:
        pass
