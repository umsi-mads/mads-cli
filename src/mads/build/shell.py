"""
Helpers for running subprocess commands
"""

# pylint: disable=raise-missing-from

import os
import time
import shlex
import select
import subprocess
from pathlib import Path

from . import log
from .logging import LSS_END

BUILD_ROOT = Path(".").resolve()


def shell(cmd: str, raise_on_error: bool = True, silent: bool = False, **kwargs) -> str:
    """Run a command and return a string of it's output."""

    res = proc(cmd, silent, **kwargs)

    # We're usually requiring processes to exit successfully.
    if raise_on_error:
        res.check_returncode()

    return res.stdout.decode("utf-8").strip()


def proc(cmd: str, silent: bool = True, **kwargs) -> subprocess.CompletedProcess:
    """Like shell, but return the process object."""

    # Prepare the command to be printed
    printcmd = cmd
    if "cwd" in kwargs:
        printdir = str(kwargs["cwd"]).replace(str(BUILD_ROOT), ".")
        printcmd = f"cd {printdir} && {cmd}"
    if not silent:
        log.info("[shell] %s", printcmd)
        log.indent()

    # Run the process
    start = time.time()
    res = _stream_process(cmd, silent, **kwargs)
    delta = time.time() - start

    # Close out the logging indent.
    if not silent:
        log.outdent()
        log.info(
            "%s Completed with code %s after %0.2f seconds",
            LSS_END,
            res.returncode,
            delta,
        )
        log.info("")

    return res


def _stream_process(cmd: str, silent: bool, **kwargs):

    kwargs.setdefault("encoding", "utf-8")
    kwargs.setdefault("shell", True)
    kwargs.setdefault("stdout", subprocess.PIPE)
    kwargs.setdefault("stderr", subprocess.PIPE)

    with subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE if "input" in kwargs else subprocess.DEVNULL,
        **kwargs,
    ) as process:

        # Configure the IO/streams
        if process.stdin:
            if kwargs.get("input"):
                process.stdin.write(kwargs["input"])
                process.stdin.close()

        # Don't block on stdout/stderr
        if process.stdout:
            os.set_blocking(process.stdout.fileno(), False)
        if process.stderr:
            os.set_blocking(process.stderr.fileno(), False)

        # Collect the output streams
        stdout = ""
        stderr = ""

        def noop(*_):
            pass

        log_fn = log.info if not silent else noop

        def communicate(proc):
            """Read stdin and stdout from a process as streams."""
            nonlocal stdout, stderr

            outputs = list(filter(None, [proc.stdout, proc.stderr]))

            # Select will return a list of only files ready to read from
            ready, _, _ = select.select(outputs, [], [], 0.0001)
            for stream in ready:
                lines = [line.rstrip() for line in stream.readlines()]
                for line in lines:
                    if stream == process.stdout:
                        log_fn("  %s", line)
                        stdout += line + "\n"
                    else:
                        log_fn("* %s", line)
                        stderr += line + "\n"

        # While the process is alive, read it's output streams
        while process.poll() is None:
            communicate(process)

        # Check one last time to see if there's anything left to get
        communicate(process)

        return subprocess.CompletedProcess(
            shlex.split(cmd), process.returncode, stdout.encode(), stderr.encode()
        )
