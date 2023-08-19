# YouTube Crawler

A powerful, asynchronous web crawler designed specifically for YouTube. Built to efficiently interact with web pages in a headless mode, this tool facilitates the seamless extraction of YouTube video comments and video information directly from the platform.

## Features

- **Asynchronous Crawling**: Uses Python's asynchronous features for fast and efficient data extraction.
- **Headless Interaction**: Operates seamlessly without opening a web browser.
- **Modular Design**: Built with modularity in mind, allowing for easy extension and maintenance.

## Modules

### 1. YoutubeCommentCrawler

Extract comments from any given YouTube video. 

#### Usage:

```python
from youtube_crawler import YoutubeCommentCrawler

with YoutubeCommentCrawler() as crawler:
    comments = await crawler.crawl('YOUR_YOUTUBE_VIDEO_URL', n_target=NUMBER_OF_COMMENTS_TO_FETCH)
```

### 2. YoutubeVideoInfoCrawler

Search for videos based on a keyword and extract their information.

#### Usage:

```python
from youtube_crawler import YoutubeVideoInfoCrawler

with YoutubeVideoInfoCrawler() as crawler:
    videos_info = await crawler.crawl('YOUR_SEARCH_TERM', n_target=NUMBER_OF_VIDEOS_TO_FETCH, filter_options=YOUR_FILTER_OPTIONS)
```

## Getting Started

1. **Clone the repository**

    ```bash
    git clone https://github.com/stevieflyer/youtube_crawler.git
    ```

2. **Navigate to the project directory**

    ```bash
    cd youtube_crawler
    ```

3. **Install the dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Start crawling**

    Use the examples provided in the modules section above.

## Contributing

Contributions are welcome! Please raise an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Happy crawling! :)
    

