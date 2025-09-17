import psutil


def find_process_on_port(port: int):
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        connections = proc.net_connections(kind="inet")
        for conn in connections:
            if conn.laddr.port == int(port):
                return proc
    return None


def kill_process_on_port(port) -> int | None:
    """
    强制释放占用指定端口的进程。

    :param port: 要释放的端口号
    """
    p = find_process_on_port(port)
    if p and (pid := p.pid):
        p.kill()
        return pid
    return None
