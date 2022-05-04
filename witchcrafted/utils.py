"""Useful utility functions."""

from random import choice
import asyncio
import concurrent.futures
import colorlog
from colorlog import ColoredFormatter
from pathlib import Path
import traceback
import sys

try:
    import winreg
except Exception:
    winreg = None


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


log_colorized = False


def set_up_logger(logger):
    """
    Set up the logger to use color.

    Only call this once.
    """
    global log_colorized
    if not log_colorized:
        log_colorized = True
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
    logger = set_up_logger(logger)
    return logger


logger = make_logger(__name__)

sanatize_map = dict((ord(char), None) for char in r'\/*?:"<>|')
sanatize_map[" "] = "_"


def sanatize_text(text):
    """Sanatize a string for saveing."""
    text = text.lower()
    return text.translate(sanatize_map)


def get_steam_paths():
    """Find a steam path with masterduel."""
    steam_paths = []
    # ==== WINDOWS ====
    # Check for steam via windows registery
    if winreg is not None:
        try:
            hkey = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"
            )
        except Exception:
            hkey = None
        if not hkey:
            try:
                hkey = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Valve.PlayOnLinux/wineprefix/PrefixName\Steam",
                )
            except Exception:
                hkey = None
        if hkey:
            try:
                steam_path = winreg.QueryValueEx(hkey, "InstallPath")
            except Exception:
                steam_path = None
            if steam_path:
                steam_path = Path(steam_path)
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
    # ==== LINUX ====
    home = Path.home()
    # Check for playonlinux
    with home.joinpath(".PlayOnLinux", "wineprefix") as playonlinux:
        if playonlinux.exists():
            logger.info("Play on linux found")
            for prefix in playonlinux.iterdir():
                steam_path = prefix.joinpath("drive_c", "Program Files (x86)", "Steam")
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
                steam_path = prefix.joinpath("drive_c", "Program Files", "Steam")
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)

    with home.joinpath(".local", "share", "bottles", "bottles") as bottles:
        if bottles.exists():
            logger.info("Bottles found")
            for prefix in bottles.iterdir():
                steam_path = prefix.joinpath("drive_c", "Program Files (x86)", "Steam")
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
                steam_path = prefix.joinpath("drive_c", "Program Files", "Steam")
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)

    # ==== MACOS ====
    # Playonmac
    with home.joinpath("Library", "PlayOnMac", "wineprefix") as playonmac:
        if playonmac.exists():
            logger.info("Play on mac found")
            for prefix in playonmac.iterdir():
                steam_path = prefix.joinpath("drive_c", "Program Files (x86)", "Steam")
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
                steam_path = prefix.joinpath("drive_c", "Program Files", "Steam")
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
    # Check for  wineskin apps that contain steam (macos)
    root = Path(home.root)
    with root.joinpath("Applications") as applications_root:
        if applications_root.exists():
            for app in applications_root.iterdir():
                steam_path = app.joinpath(
                    "Contents", "Resources", "drive_c", "Program Files (x86)", "Steam"
                )
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
                steam_path = app.joinpath(
                    "Contents", "Resources", "drive_c", "Program Files", "Steam"
                )
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
    with home.joinpath("Applications") as applications_home:
        if applications_home.exists():
            for app in applications_home.iterdir():
                steam_path = app.joinpath(
                    "Contents", "Resources", "drive_c", "Program Files (x86)", "Steam"
                )
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)
                steam_path = app.joinpath(
                    "Contents", "Resources", "drive_c", "Program Files", "Steam"
                )
                if steam_path.exists():
                    logger.info(f"Steam found at: {steam_path}")
                    steam_paths.append(steam_path)

    # ### LINUX/MACOS ######
    # Check for wine
    with home.joinpath(".wine") as wine_path:
        if wine_path.exists():
            logger.info("Wine found")
            steam_path = wine_path.joinpath("drive_c", "Program Files (x86)", "Steam")
            if steam_path.exists():
                logger.info(f"Steam found at: {steam_path}")
                steam_paths.append(steam_path)
            steam_path = wine_path.joinpath("drive_c", "Program Files", "Steam")
            if steam_path.exists():
                logger.info(f"Steam found at: {steam_path}")
                steam_paths.append(steam_path)
    # Check for wine64
    with home.joinpath(".wine64") as wine64_path:
        if wine_path.exists():
            logger.info("Wine64 found")
            steam_path = wine64_path.joinpath("drive_c", "Program Files (x86)", "Steam")
            if steam_path.exists():
                logger.info(f"Steam found at: {steam_path}")
                steam_paths.append(steam_path)
            steam_path = wine64_path.joinpath("drive_c", "Program Files", "Steam")
            if steam_path.exists():
                logger.info(f"Steam found at: {steam_path}")
                steam_paths.append(steam_path)
    return steam_paths


def get_md_paths():
    """Get all masterduel path directories."""
    md_paths = []
    steam_paths = get_steam_paths()
    for steam_path in steam_paths:
        md_path = steam_path.joinpath("steamapps", "common", "Yu-Gi-Oh!  Master Duel")
        if md_path.exists():
            logger.info(f"Masterduel found at {md_path}")
            md_paths.append(md_path)
    return md_paths


def data_dir():
    """Get the TLD of the data."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        tld = Path(sys._MEIPASS)
    else:
        tld = Path.cwd()
        if not (tld / "assets").exists():
            tld = Path(__file__).parent.parent
    return tld


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
        cls.__instance.loop.set_exception_handler(cls.__instance.handle_exception)
        return cls.__instance

    def handle_exception(self, loop, context):
        """Handle an asyncio error."""
        e = context.get("exception", None)
        if e is not None:
            self.shutdown()
            if isinstance(e, KeyboardInterrupt):
                pass
            else:
                extype = type(e)
                tb = "".join(traceback.format_exception(None, e, e.__traceback__))
                logger.error(f"Error: {extype}\n{e}\n\n{tb}")

        else:
            logger.warn(context["message"])

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

    def async_future(self):
        """Create an async future."""
        return self.loop.create_future()

    def async_finish_future(self, future, value):
        """Finish an async future."""
        return self.loop.call_soon_threadsafe(future.set_result, value)

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
