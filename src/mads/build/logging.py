"""
Configure logging for the build and define helper functions.
"""

import sys
import time
import logging
from typing import List, Union
from pathlib import Path
from datetime import datetime, timedelta

LSS_START = "┌"
LSS_END = "└"
LOG_FILE = Path("build-log.txt")
DATA_SUFFIXES = ["B", "KB", "MB", "GB", "TB", "PB"]


class BuildLogger(logging.LoggerAdapter):
    """Indent log statements based on the current nesting level"""

    _indent: List[str] = []

    def __init__(self, logger):
        super().__init__(logger, {})

    @property
    def file(self) -> Path:
        """The file to log to"""

        return LOG_FILE

    def process(self, msg, kwargs):
        """Prepend the log statement with all the indent chars"""
        return " ".join([*self._indent, msg]), kwargs

    def log(self, level, msg, *args, **kwargs):
        """Split multi-line log messages into separate calls so we include the prefix."""
        if self.isEnabledFor(level):
            if args:
                msg = msg % args
            for line in msg.split("\n"):
                if level >= logging.WARNING:
                    line = f"{logging.getLevelName(level)}: {line}"
                line, kwargs = self.process(line, kwargs)
                self.logger.log(level, line, *[], **kwargs)

    def indent(self, char: str = "│"):
        """Increase the indent"""
        self._indent.append(char)

    def outdent(self):
        """Decrease the indent"""
        self._indent.pop(-1)

    def tree(
        self,
        pwd: Union[str, Path] = ".",
        *,
        size: bool = True,
        mtime: bool = False,
    ):
        """Print the file tree starting at the given directory."""

        root: Path = pwd if isinstance(pwd, Path) else Path(pwd)
        self.info("[tree] %s", root.resolve())

        def _tree(root: Path):
            self.indent("   ")
            children = list(root.iterdir())

            # Put files first
            children.sort(key=lambda x: (not x.is_file(), x.name))

            for child in children:
                if child.name in [".git", "build", ".pytest_cache", "__pycache__"]:
                    self.info("%s -- skipping contents for brevity", child.name)
                    continue

                if child.is_file():
                    if size:
                        sizestr = human_size(child.stat().st_size)
                    else:
                        sizestr = None

                    if mtime:
                        mtimestr = "mod " + human_time_distance(
                            datetime.fromtimestamp(child.stat().st_mtime)
                        )
                    else:
                        mtimestr = None

                    if sizestr or mtimestr:
                        suffix = (
                            " (" + ", ".join(filter(None, [sizestr, mtimestr])) + ")"
                        )
                    else:
                        suffix = ""

                elif child.is_symlink():
                    suffix = " -> " + str(child.resolve())
                elif child.is_dir():
                    suffix = "/"
                else:
                    suffix = " (?)"

                self.info("%s%s", child.name, suffix)

                if child.is_dir():
                    _tree(child)

            self.outdent()

        _tree(root)
        self.info("")

    def report_runtime(self, func):
        """Log information about the start and finish of a function."""

        def wrapper(*args, **kwargs):
            name = func.__name__
            self.info("%s Starting function %s", LSS_START, name)
            self.indent()
            self.info("")
            start = time.time()
            res = func(*args, **kwargs)
            delta = time.time() - start
            self.info("")
            self.outdent()
            self.info(
                "%s Completed function %s after %0.2f seconds", LSS_END, name, delta
            )
            self.info("")
            return res

        return wrapper


def init_logging() -> BuildLogger:
    """Set up exec environment, namely logging."""

    # Reset both loggers
    root = logging.getLogger()
    mlog = logging.getLogger("mads")
    for logger in [root, mlog]:
        for handler in logger.handlers:
            root.removeHandler(handler)

    # Add a null handler to prevent it from being populated automatically
    root.addHandler(logging.NullHandler())

    # Set up the handlers we want to use
    fmt = logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] %(message)s", datefmt="%H:%M:%S"
    )
    cout = logging.StreamHandler(stream=sys.stderr)
    fout = logging.FileHandler(LOG_FILE)

    # Configure our logger with those handlers
    mlog.setLevel(logging.DEBUG)
    for out in [cout, fout]:
        out.setFormatter(fmt)
        out.setLevel(logging.DEBUG)
        mlog.addHandler(out)

    return BuildLogger(mlog)


log = init_logging()


def human_size(nbytes: float | int) -> str:
    """Returns a human representation of a number of bytes.
    Adapted from https://stackoverflow.com/a/14996816/1893290
    """
    i = 0
    while nbytes >= 1024 and i < len(DATA_SUFFIXES) - 1:
        nbytes /= 1024.0
        i += 1

    # Strip any needless decimal places
    display = f"{nbytes:.2f}".rstrip("0").rstrip(".")

    # Attach the correct unit
    return f"{display} {DATA_SUFFIXES[i]}"


def human_time_distance(timestamp: datetime) -> str:
    duration = datetime.now() - timestamp
    past = duration.total_seconds() > 0
    suffix = "ago" if past else "from now"
    return human_duration(duration) + " " + suffix


def human_duration(duration: timedelta) -> str:
    """Returns a human representation of a timedelta."""
    seconds = abs(duration.total_seconds())
    if seconds < 0.001:
        return f"{seconds * 1000000} microseconds"
    if seconds < 1:
        return f"{seconds * 1000:.1f} milliseconds"
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hours"
    else:
        return f"{seconds / 86400:.0f} days"
