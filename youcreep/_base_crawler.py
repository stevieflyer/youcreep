import abc
import logging
import pathlib
import pandas as pd
from typing import Union, Callable

from gembox.io import ensure_pathlib_path, check_and_make_dir
from gembox.debug_utils import Debugger, FileConsoleDebugger, FileDebugger

from youcreep.page_parser import YoutubePageParser
from youcreep.browser_agent import YoutubeBrowserAgent
from multi_async import AsyncTask, ParallelAsyncRunner


class YoutubeBaseCrawler:
    def __init__(self, headless=False, debug_tool: Debugger = None,
                 interactor_config_path: Union[str, pathlib.Path] = None):
        self._browser_agent = YoutubeBrowserAgent(headless=headless, debug_tool=debug_tool,
                                                  interactor_config_path=interactor_config_path)
        self._page_parser = YoutubePageParser(browser_agent=self._browser_agent)

    @property
    async def is_running(self):
        page = await self._browser_agent.browser_manager.get_page()
        return self._browser_agent.is_running and page is not None

    async def start(self) -> None:
        await self._browser_agent.start()

    async def stop(self) -> None:
        await self._browser_agent.stop()

    @abc.abstractmethod
    def crawl(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    async def _parallel_crawl_base(cls, worker_fn, task_params, n_workers=1):
        tasks = [AsyncTask(worker_fn, params=params) for params in task_params]
        await ParallelAsyncRunner.run(tasks, n_workers=n_workers)

    @classmethod
    async def _generic_worker(cls,
                              log_filename_func: Callable[..., str],
                              data_filename_func: Callable[..., str],
                              output_dir: Union[str, pathlib.Path],
                              verbose: bool,
                              **crawl_args) -> None:
        """
        Generic worker function to crawl data and save it.
        :param log_filename_func: Function to generate log filename based on arguments.
        :param data_filename_func: Function to generate data filename based on arguments.
        :param output_dir: Output directory.
        :param verbose: Whether to print debug messages.
        :param crawl_args: Arguments for the crawl operation.
        """
        output_dir = ensure_pathlib_path(output_dir)
        log_dir = output_dir / "logs"
        check_and_make_dir(log_dir)
        check_and_make_dir(output_dir)
        log_path = log_dir / log_filename_func(**crawl_args)
        data_path = output_dir / data_filename_func(**crawl_args)
        debugger = FileConsoleDebugger(filepath=log_path, level=logging.INFO) if verbose else FileDebugger(filepath=log_path, level=logging.INFO)

        try:
            async with cls(debug_tool=debugger, headless=True) as crawler:
                results = await crawler.crawl(**crawl_args)
                df = pd.DataFrame([result.to_dict() for result in results])
                df.to_csv(data_path)
        except Exception as e:
            debugger.error(f"Error while crawling. Error: {str(e)}")

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


__all__ = ["YoutubeBaseCrawler"]
