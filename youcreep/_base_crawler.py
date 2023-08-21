import abc
import logging
import pathlib
import pandas as pd
from typing import Union, Callable, List, Dict

from gembox.io import ensure_pathlib_path, check_and_make_dir
from gembox.debug_utils import Debugger, FileConsoleDebugger, FileDebugger

from youcreep.page_parser import YoutubePageParser
from youcreep.browser_agent import YoutubeBrowserAgent
from gembox.multiprocess.mp_async import AsyncTask, ParallelAsyncRunner


class YoutubeBaseCrawler:
    def __init__(self, headless=False, debug_tool: Debugger = None,
                 interactor_config_path: Union[str, pathlib.Path] = None):
        self._browser_agent = YoutubeBrowserAgent(headless=headless, debug_tool=debug_tool,
                                                  interactor_config_path=interactor_config_path)
        self._page_parser = YoutubePageParser(browser_agent=self._browser_agent)

    @property
    async def is_running(self):
        """whether the crawler is running"""
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
    async def parallel_crawl(cls,
                             param_dict_list: List[Dict],
                             n_workers: int = 1,
                             verbose: bool = False,
                             headless: bool = True) -> None:
        """
        Parallel crawl function for YoutubeVideoInfoCrawler using parameter dictionaries.

        :param param_dict_list: List of parameter dictionaries
        :param n_workers: Number of parallel workers.
        :param verbose: Whether to print the log.
        :param headless: Whether to run the browser in headless mode.
        """
        # 1. Parameter validation, the key must be one of the async def crawl's parameters
        required_fields = cls.required_fields()
        optional_fields = cls.optional_fields()
        all_fields = cls.all_fields()

        assert len(param_dict_list) > 0, "The parameter list must not be empty."
        for param_dict in param_dict_list:
            for key, value in param_dict.items():
                assert key in required_fields or key in optional_fields, f"Invalid parameter key {key}, required fields are {required_fields.keys()}, optional fields are {optional_fields.keys()}."
                assert isinstance(value, all_fields[key]), f"Invalid parameter type for key {key}, expected type is {all_fields[key]}, got {type(value)}."

        # 获取除去了 output_dir 的 **kwargs
        _kwargs = {key: value for key, value in param_dict_list[0].items() if key != "output_dir"}
        file_name = "".join([f"{key}_{value}_" for key, value in _kwargs.items()]) + cls.__name__.lower()

        # 2. Create task parameters
        task_params = [
            {
                "log_filename_func": lambda **kwargs: f"{cls._save_name(kwargs)}.log",
                "data_filename_func": lambda **kwargs: f"{cls._save_name(kwargs)}.csv",
                "verbose": verbose,
                "headless": headless,
                # children class specific parameters
                **param,
            }
            for param in param_dict_list
        ]

        await cls._parallel_crawl_base(worker_fn=cls._generic_worker, task_params=task_params, n_workers=n_workers)

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
                              headless: bool,
                              **crawl_args) -> None:
        """
        Generic worker function: crawl data and save it.

        :param log_filename_func: Function to generate log filename based on arguments.
        :param data_filename_func: Function to generate data filename based on arguments.
        :param output_dir: Output directory.
        :param verbose: Whether to print debug messages.
        :param headless: Whether to run the browser in headless mode.
        :param crawl_args: Arguments for the crawl operation.
        """
        output_dir = ensure_pathlib_path(output_dir)
        log_dir = output_dir / "logs"
        check_and_make_dir(log_dir)
        check_and_make_dir(output_dir)
        log_path = log_dir / log_filename_func(**crawl_args)
        data_path = output_dir / data_filename_func(**crawl_args)
        debugger = FileConsoleDebugger(filepath=log_path, level=logging.INFO) if verbose else FileDebugger(filepath=log_path, level=logging.INFO)

        finished = False
        n_retry, max_retry = 0, 3
        while n_retry < max_retry and not finished:
            try:
                async with cls(debug_tool=debugger, headless=headless) as crawler:
                    results = await crawler.crawl(**crawl_args)
                    df = pd.DataFrame([result.to_dict() for result in results])
                    df.to_csv(data_path)
                    finished = True
            except Exception as e:
                debugger.error(f"Error while crawling. Error: {str(e)}")
                debugger.warn(f"Retrying {n_retry + 1}/{max_retry}...")
                n_retry += 1

    @classmethod
    @abc.abstractmethod
    def required_fields(cls) -> Dict:
        """
        Required fields for the parameter dictionary used in parallel crawl.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def optional_fields(cls) -> Dict:
        """
        Optional fields for the parameter dictionary used in parallel crawl.
        """
        pass

    @classmethod
    def all_fields(cls) -> Dict:
        """
        All fields for the parameter dictionary used in parallel crawl.
        """
        return {**cls.required_fields(), **cls.optional_fields()}

    @classmethod
    def _save_name(cls, _kw: dict) -> str:
        _kwargs = {key: value for key, value in _kw.items() if key != "output_dir"}
        file_name = "".join([f"{key}_{value}_" for key, value in _kwargs.items()]) + cls.__name__.lower()
        return file_name

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


__all__ = ["YoutubeBaseCrawler"]
