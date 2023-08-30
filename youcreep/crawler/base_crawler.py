import abc
import logging
import pathlib
import traceback
from typing import List, Dict

from gembox.debug_utils import Debugger, FileConsoleDebugger, FileDebugger
from gembox.io import ensure_pathlib_path, check_and_make_dir
from gembox.multiprocess import Task, ParallelExecutor

from youcreep.browser_agent import YoutubeAgent


class YoutubeBaseCrawler(abc.ABC):
    """
    Crawler for video info on YouTube.

    Crawler is responsible for interacting with the browser agent until some requirements are satisfied.

    Then the crawler download the page and save it to the disk.
    """
    def __init__(self, browser_agent: YoutubeAgent, debug_tool: Debugger):
        self._browser_agent = browser_agent
        self._debug_tool = debug_tool

    @abc.abstractmethod
    async def crawl(self, *args, **kwargs):
        raise NotImplementedError

    async def start(self):
        if self.is_running:
            self.debug_tool.warn("YoutubeBaseCrawler is already running. No need to start again")
            return
        self.debug_tool.info(f"Starting YoutubeBaseCrawler...")
        await self.browser_agent.start()
        self.debug_tool.info(f"Start YoutubeBaseCrawler successfully")

    async def stop(self):
        if self.is_running is False:
            self.debug_tool.warn("YoutubeBaseCrawler is not running. No need to stop")
            return
        self.debug_tool.info(f"Stopping YoutubeBaseCrawler...")
        await self.browser_agent.stop()
        self.debug_tool.info(f"Stop YoutubeBaseCrawler successfully")

    @classmethod
    async def instantiate(cls, headless=False, debug_tool: Debugger = None) -> 'YoutubeBaseCrawler':
        debug_tool = Debugger() if debug_tool is None else debug_tool
        browser_agent = await YoutubeAgent.instantiate(headless=headless, debug_tool=debug_tool)
        instance = cls(browser_agent=browser_agent, debug_tool=debug_tool)
        return instance

    @property
    def browser_agent(self) -> YoutubeAgent:
        return self._browser_agent

    @property
    def debug_tool(self) -> Debugger:
        return self._debug_tool

    @property
    def is_running(self) -> bool:
        return self.browser_agent.is_running

    @classmethod
    async def parallel_crawl(cls,
                             crawl_args_list: List[Dict],
                             output_dir: (str, pathlib.Path),
                             verbose: bool = False,
                             max_retry: int = 5,
                             n_workers: int = 1,
                             headless: bool = True) -> None:
        """
        Parallel crawl function for YoutubeVideoInfoCrawler using parameter dictionaries.

        :param crawl_args_list: (list<dict>) List of parameter dictionaries
        :param output_dir: (str, pathlib.Path) the directory to save the crawled data
        :param n_workers: (int) Number of parallel workers.
        :param max_retry: (int) maximum number of retry
        :param verbose: (bool) Whether to print the log.
        :param headless: (bool) Whether to run the browser in headless mode.
        """
        # 1. Parameter validation, the key must be one of the async def crawl's parameters
        assert len(crawl_args_list) > 0, "The parameter list must not be empty."
        for crawl_args in crawl_args_list:
            crawl_args = {**crawl_args, "save_dir": output_dir}
            cls._validate_crawl_args(**crawl_args)

        # 2. Create task parameters
        worker_args_list = [
            {
                **crawl_args,
                "output_dir": output_dir,
                "verbose": verbose,
                "headless": headless,
                "max_retry": max_retry,
            }
            for crawl_args in crawl_args_list
        ]

        tasks = [Task(cls._crawl_worker, params=worker_args) for worker_args in worker_args_list]
        await ParallelExecutor.run(tasks, n_workers=n_workers)

    @classmethod
    async def _crawl_worker(cls,
                            output_dir: (str, pathlib.Path),
                            verbose: bool,
                            headless: bool,
                            max_retry: int = 5,
                            **crawl_args) -> None:
        """
        Generic crawler worker for building parallel crawler.

        :param output_dir: (str, pathlib.Path) the directory to save the crawled data
        :param verbose: (bool) whether to print the log to the console
        :param headless: (bool) whether the browser is headless
        :param max_retry: (int) maximum number of retry
        :param crawl_args: (dict) the arguments for the crawler
        :return: (None)
        """
        # 0. 参数检查
        assert isinstance(max_retry, int) and max_retry > 0, f"max_retry must be a positive integer, got {max_retry}"
        crawl_args = {
            **crawl_args,
            "save_dir": output_dir,  # output_dir 将覆写 crawl_args 中的 save_dir
        }
        cls._validate_crawl_args(**crawl_args)
        file_name = cls._file_name(**crawl_args)  # 生成文件名, 用于命名 log 文件, html 文件

        output_dir = ensure_pathlib_path(output_dir)
        log_dir = output_dir / "logs"
        check_and_make_dir(log_dir)
        check_and_make_dir(output_dir)
        log_path = log_dir / f"{file_name}.log"
        debugger = FileConsoleDebugger(filepath=log_path, level=logging.INFO) if verbose else FileDebugger(filepath=log_path, level=logging.INFO)

        finished = False
        n_retry = 0
        while n_retry < max_retry and not finished:
            crawler = None
            try:
                crawler = await cls.instantiate(debug_tool=debugger, headless=headless)
                async with crawler:
                    await crawler.crawl(**crawl_args)
                    finished = True
            except Exception as e:
                if crawler is not None:
                    debugger.info(f"Stopping crawler... in except")
                    await crawler.stop()
                else:
                    debugger.info(f"Crawler is None... in except")
                error_message = str(e)
                stack_trace = traceback.format_exc()
                debugger.error(f"Error while crawling. Error: {error_message}")
                debugger.error(f"Stack Trace: {stack_trace}")
                debugger.warn(f"Retrying {n_retry + 1}/{max_retry}...")
                n_retry += 1
            debugger.info(f"Finished after {n_retry}/{max_retry} retrie, finished_flag: {finished}")

    @classmethod
    def _validate_crawl_args(cls, **crawl_args):
        # for each required_field, it must be contained in crawl_args
        for field_name, field_type in cls.required_fields().items():
            assert field_name in crawl_args, f"{field_name} is required, but not found in crawl_args."
            assert isinstance(crawl_args[field_name], field_type), f"{field_name} should be {field_type}, but got {crawl_args[field_name].__class__.__name__}"

        # for each optional_field, it can be ommited in the crawl_args
        for field_name, field_type in cls.optional_fields().items():
            if field_name in crawl_args:
                assert isinstance(crawl_args[field_name], field_type), f"{field_name} should be {field_type}, but got {crawl_args[field_name].__class__.__name__}"

    @classmethod
    @abc.abstractmethod
    def _file_name(cls, **kwargs) -> str:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def required_fields(cls) -> dict:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def optional_fields(cls) -> dict:
        raise NotImplementedError

    @classmethod
    def crawler_fields(cls) -> dict:
        return {
            **cls.required_fields,
            **cls.optional_fields,
        }

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
