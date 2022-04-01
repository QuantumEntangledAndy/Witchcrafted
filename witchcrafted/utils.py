"""Useful utility functions."""

from random import choice
import asyncio
import concurrent.futures
import colorlog
from colorlog import ColoredFormatter


def multiline_strip(text):
    """Strip extra chars from every line."""
    return "\n".join(map(lambda x: x.strip(), text.strip().split("\n")))


def random_color():
    """Generate a random color string."""
    hex_string = "0123456789abcdef"
    return "#" + "".join([choice(hex_string) for x in range(6)])


def clamp(num, min_value, max_value):
    """Clamp a value."""
    return max(min(num, max_value), min_value)


def set_up_logger(logger):
    """
    Set up the logger to use color.

    Only call this once.
    """
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(white)s%(message)s",
        datefmt="None",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )
    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel("DEBUG")
    return logger


def make_logger(name):
    """Make a logger."""
    logger = colorlog.getLogger(name)
    return logger


logger = make_logger(__name__)


class Async(object):
    """Object to handle asyncio and threadpool threads."""

    __instance = None

    def __new__(cls):
        """Create the singleton."""
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        cls.__instance.async_tasks = []
        cls.__instance.thread_tasks = []
        cls.__instance.loop = asyncio.get_event_loop()
        cls.__instance.excecutor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        # cls.__instance.loop.set_exception_handler(cls.__instance.handle_exception)
        return cls.__instance

    def async_fire(self, task):
        """Run a task in async but don't handle a handle to it."""
        if self.loop is not None:
            handle = self.loop.create_task(task)
            return handle
        else:
            return None

    def async_task(self, task):
        """Run an asyncio task."""
        handle = self.async_fire(task)
        if handle is not None:
            self.async_tasks.append(handle)
        return handle

    async def async_thread(self, task):
        """Run an thread and async await its completion."""
        task = self.thread_task(task)
        while not task.done():
            await asyncio.sleep(0.01)

        try:
            return task.result()
        except concurrent.futures.CancelledError:
            return None
        except Exception as e:
            raise e

    def thread_fire(self, task):
        """Run an thread task on the pool but don't handle a handle to it."""
        if self.excecutor is not None:
            handle = self.excecutor.submit(task)
        return handle

    def thread_task(self, task):
        """Run an thread task on the pool."""
        handle = self.thread_fire(task)
        if handle is not None:
            self.thread_tasks.append(handle)
        return handle

    def shutdown(self):
        """Shutdown the async and threadpool."""
        self.async_fire(self.shutdown_async())

    async def shutdown_async(self):
        """Shutdown the async and threadpool."""
        if self.loop is not None:
            # Cancel asyncio
            for task in self.async_tasks:
                task.cancel()
            # Await clean exit
            interval = 0.01
            while any(map(lambda x: not x.done(), self.async_tasks)):
                await asyncio.sleep(interval)
            self.loop.stop()
            self.loop = None

        if self.excecutor is not None:
            # Cancel all thread pools
            for task in self.thread_tasks:
                task.cancel()

            self.excecutor.shutdown(wait=True, cancel_futures=True)
            self.excecutor = None

    def run(self):
        """Run the loop."""
        loop = self.loop
        loop.run_forever()
        loop.close()
