import logging
from pathlib import Path
from typing import List

import psutil
from ipa.decorator import deprecated


@deprecated("请使用 find_all_process_on_port 替代")
def find_process_on_port(port: int):
    """
    查找占用指定端口的进程，如果有多个只返回第一个。
    """
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        connections = proc.net_connections(kind="inet")
        for conn in connections:
            if conn.laddr.port == int(port):
                return proc
    return None


@deprecated("请使用 kill_all_process_on_port 替代")
def kill_process_on_port(port, max_try: int | None = 1) -> int | None:
    """
    强制释放占用指定端口的进程，如果有多个进程只处理第一个。

    Args:
        port (int): 要释放的端口号
        max_try (int, optional): 最大尝试次数。值为 None，代表无限次尝试。

    Returns:
        int | None: 成功释放进程的 PID，如果不存在对应进程则返回 None。
    """
    pid: int | None = None
    try_count = 0
    while max_try is None or try_count < max_try:
        p = find_process_on_port(port)
        if not p or not p.pid:
            return pid
        pid = p.pid
        try:
            p.kill()
            logging.info("process on port %s been killed: %s", port, pid)
            return pid
        except Exception as e:
            try_count += 1
            logging.warning(
                "kill process on port %s failed(x%s): %s", port, try_count, e
            )
    raise RuntimeError(f"kill process on port {port} failed after {try_count} times")


def find_all_process_on_port(port: int) -> List[psutil.Process]:
    """
    查找占用指定端口的所有进程。
    """
    procs = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        connections = proc.net_connections(kind="inet")
        for conn in connections:
            if conn.laddr.port == int(port):
                procs.append(proc)
    return procs


def kill_all_process_on_port(port, max_try: int | None = 1) -> int | None:
    """
    强制释放占用指定端口的所有进程。

    Args:
        port (int): 要释放的端口号
        max_try (int, optional): 最大尝试次数。值为 None，代表无限次尝试。

    Returns:
        int | None: 成功释放进程的 PID，如果不存在对应进程则返回 None。
    """

    def _kill(p: psutil.Process):
        pid: int | None = None
        try_count = 0
        while max_try is None or try_count < max_try:
            if not p or not p.pid:
                return pid
            pid = p.pid
            try:
                p.kill()
                logging.info("process on port %s been killed: %s", port, pid)
                return pid
            except Exception as e:
                try_count += 1
                logging.warning(
                    "kill process on port %s failed(x%s): %s", port, try_count, e
                )
        raise RuntimeError(
            f"kill process on port {port} failed after {try_count} times"
        )

    ps = find_all_process_on_port(port)
    for p in ps:
        _kill(p)


def ensure_path(path: str | Path):
    return Path(path)
    # return path if isinstance(path, Path) else Path(path)
