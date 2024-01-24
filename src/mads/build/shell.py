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


def shell(cmd: str, raise_on_error: bool = True, **kwargs) -> str:
    """Run a command and return a string of it's output."""

    res = proc(cmd, **kwargs)

    # We're usually requiring processes to exit successfully.
    if raise_on_error:
        res.check_returncode()

    return res.stdout.decode("utf-8").strip()


def proc(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    """Like shell, but return the process object."""

    # Prepare the command to be printed
    printcmd = cmd
    if "cwd" in kwargs:
        printdir = str(kwargs["cwd"]).replace(str(BUILD_ROOT), ".")
        printcmd = f"cd {printdir} && {cmd}"
    log.info("[shell] %s", printcmd)
    log.indent()

    # Run the process
    start = time.time()
    res = _stream_process(cmd, **kwargs)
    delta = time.time() - start

    # Close out the logging indent.
    log.outdent()
    log.info(
        "%s Completed with code %s after %0.2f seconds", LSS_END, res.returncode, delta
    )
    log.info("")

    return res


def _stream_process(cmd, **kwargs):
    with subprocess.Popen(
        cmd,
        encoding="utf-8",
        stdin=subprocess.PIPE if "input" in kwargs else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=kwargs.get("cwd"),
    ) as process:
        stdout = ""
        stderr = ""

        if kwargs.get("input"):
            process.stdin.write(kwargs["input"])
            process.stdin.close()

        # Don't block on stdout/stderr
        os.set_blocking(process.stdout.fileno(), False)
        os.set_blocking(process.stderr.fileno(), False)

        def communicate(proc):
            """Read stdin and stdout from a process as streams."""
            nonlocal stdout, stderr

            outputs = [proc.stdout, proc.stderr]

            # Select will return a list of only files ready to read from
            ready, _, _ = select.select(outputs, [], [], 0.0001)
            for stream in ready:
                lines = [line.rstrip() for line in stream.readlines()]
                for line in lines:
                    if stream == process.stdout:
                        log.info("  %s", line)
                        stdout += line + "\n"
                    else:
                        log.info("* %s", line)
                        stderr += line + "\n"

        # While the process is alive, read it's output streams
        while process.poll() is None:
            communicate(process)

        # Check one last time to see if there's anything left to get
        communicate(process)

        return subprocess.CompletedProcess(
            shlex.split(cmd), process.returncode, stdout.encode(), stderr.encode()
        )
