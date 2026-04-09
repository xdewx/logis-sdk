import logging
import time
from pathlib import Path
from typing import List, Optional, Union

from ipa.system import (
    find_all_process_on_port,
    find_and_kill_process,
    find_process,
    find_process_on_port,
    get_disk_usage,
    kill_all_process_on_port,
    wait_port_idle,
)


def ensure_path(path: Union[str, Path]):
    return Path(path)
    # return path if isinstance(path, Path) else Path(path)
