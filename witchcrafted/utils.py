"""Useful utility functions."""

from tkinter import ttk
from enum import Enum
from itertools import zip_longest
from random import randint, choice
import asyncio
import concurrent.futures


def grouper(iterable, n, *, incomplete="fill", fillvalue=None):
    """Collect data into non-overlapping fixed-length chunks or blocks."""
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    if incomplete == "fill":
        return zip_longest(*args, fillvalue=fillvalue)
    if incomplete == "strict":
        return zip(*args, strict=True)
    if incomplete == "ignore":
        return zip(*args)
    else:
        raise ValueError("Expected fill, strict, or ignore")


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


class MainFrames(Enum):
    """Enum of the primary app frames."""

    SETUP = 1
    CARDS = 2


class AppFrame(ttk.Frame):
    """A frame that setsup various app related properties."""

    def __init__(self, container, *args, **kwargs):
        """Init the frame."""
        super().__init__(container, *args, **kwargs)
        self.settings = container.settings
        self.app = container.app
        self.parent = container

        # for col in range(0, 20):
        #     self.columnconfigure(col, weight=1)
        #     self.rowconfigure(col, weight=1)

        if self.settings.debug:
            s = ttk.Style()
            style_name = f"Frame{randint(0, 65535)}.TFrame"
            s.configure(style_name, background=random_color())
            self.configure(style=style_name)

        self.update()

    def switch_to(self, main_frame):
        """Switch the app to another primary frame."""
        self.app.main_frame = main_frame
        self.app.switch_frame()

    def reset(self):
        """Reset the frame."""
        # Should be overloaded

    async def await_size(self):
        """Wait until this frame has a size."""
        while self.winfo_width() == 1 and self.winfo_height() == 1:
            self.update()
            await asyncio.sleep(0.01)
        return (self.winfo_width(), self.winfo_height())


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

        return cls.__instance

    def async_fire(self, task):
        """Run a task in async but don't handle a handle to it."""
        handle = self.loop.create_task(task)
        return handle

    def async_task(self, task):
        """Run an asyncio task."""
        handle = self.async_fire(task)
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
        handle = self.excecutor.submit(task)
        return handle

    def thread_task(self, task):
        """Run an thread task on the pool."""
        handle = self.thread_fire(task)
        self.thread_tasks.append(handle)
        return handle

    async def shutdown(self):
        """Shutdown the async and threadpool."""
        # Cancel asyncio
        for task in self.async_tasks:
            task.cancel()
        # Await clean exit
        interval = 0.01
        while any(map(lambda x: not x.done(), self.async_tasks)):
            await asyncio.sleep(interval)
        self.loop.stop()

        # Cancel all thread pools
        for task in self.thread_tasks:
            task.cancel()

        self.excecutor.shutdown(wait=True, cancel_futures=True)

    def run(self):
        """Run the loop."""
        self.loop.run_forever()
        self.loop.close()
