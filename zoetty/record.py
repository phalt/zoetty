"""Run commands in a pseudo-terminal and capture what they print, colours and all."""

import fcntl
import os
import pty
import select
import signal
import struct
import subprocess
import termios
import time
from dataclasses import dataclass
from pathlib import Path

from zoetty.clip import Clip

# How long a command has to be quiet before the next line of `input` is typed.
QUIET = 0.3


class SetupFailed(Exception):
    def __init__(self, command: str, exit_code: int, output: str) -> None:
        self.command = command
        self.exit_code = exit_code
        self.output = output
        super().__init__(f"setup command {command!r} exited {exit_code}")


@dataclass(frozen=True)
class Result:
    exit_code: int | None
    output: bytes
    timed_out: bool = False


def environment(clip: Clip) -> dict[str, str]:
    """The environment commands are recorded in: colour on, the clip's size, no pagers."""
    rows = clip.rows or 24
    return (
        os.environ
        | {
            "TERM": "xterm-256color",
            "COLUMNS": str(clip.cols),
            "LINES": str(rows),
            "FORCE_COLOR": "1",
            "CLICOLOR_FORCE": "1",
            "PAGER": "cat",
            "GIT_PAGER": "cat",
        }
        | clip.record.env
    )


def setup(clip: Clip, env: dict[str, str]) -> None:
    """Run the clip's setup commands. Raises SetupFailed on the first that fails."""
    for command in clip.record.setup:
        done = subprocess.run(
            command,
            shell=True,
            cwd=clip.record.cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=clip.record.timeout,
        )
        if done.returncode:
            raise SetupFailed(command, done.returncode, done.stdout + done.stderr)


def run(
    command: str, *, cwd: Path, env: dict[str, str], cols: int, rows: int, input: str | None = None, timeout: float = 60
) -> Result:
    """Run a shell command in a pty sized cols x rows and return everything it wrote.

    Each line of `input` is typed once the command has been quiet for a moment, so it
    lands after the prompt that asked for it, the way a person would type it.
    """
    pending = (input or "").splitlines(keepends=True)
    primary, secondary = pty.openpty()
    fcntl.ioctl(secondary, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    process = subprocess.Popen(
        ["/bin/sh", "-c", command],
        stdin=secondary,
        stdout=secondary,
        stderr=secondary,
        cwd=cwd,
        env=env,
        start_new_session=True,
    )
    os.close(secondary)
    output = bytearray()
    deadline = time.monotonic() + timeout
    try:
        while True:
            if time.monotonic() > deadline:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                return Result(None, bytes(output), timed_out=True)
            ready, _, _ = select.select([primary], [], [], QUIET)
            if ready:
                try:
                    chunk = os.read(primary, 65536)
                except OSError:  # Linux: the command and everything it started have closed the terminal
                    chunk = b""
                if not chunk:
                    break
                output += chunk
            elif pending:
                os.write(primary, pending.pop(0).encode())
            elif process.poll() is not None:
                break
    finally:
        os.close(primary)
    return Result(process.wait(), bytes(output))
