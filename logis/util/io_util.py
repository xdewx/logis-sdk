import asyncio
import inspect
import logging
import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, Generic, List, Literal, Type

from pydantic import BaseModel, ConfigDict

from logis.data_type import T
from logis.iface import QueueType


class WriteBufferConfig(BaseModel):
    # 每批最大事件数
    batch_size: int = 256

    # 缓存的最大条目数，默认无限制
    queue_size: int = 0

    # 缓存的最大时间间隔
    flush_interval: float = 10

    queue_type: QueueType | None = None

    _queue: QueueType | None = None

    handler: Callable[[List[T]], None] | None | Coroutine[Any, Any, None] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_queue(self, mode: Literal["sync", "async"]) -> QueueType:
        if self._queue is None:
            if self.queue_type is None:
                self.queue_type = queue.Queue[T] if mode == "sync" else asyncio.Queue[T]
            self._queue = self.queue_type(maxsize=self.queue_size)
        return self._queue


class WriteBuffer(ABC, Generic[T]):
    """
    写操作缓冲器
    """

    def __init__(self, config: WriteBufferConfig, **kwargs):
        self._config = config
        self._handler = self._config.handler

        self._is_running = False
        self._last_flush_time = time.time()
        self._lock: threading.Lock | asyncio.Lock | None = None
        self._flush_task: threading.Thread | None = None

    def need_flush(self) -> bool:
        """判断是否需要刷新（根据时间间隔和条目数）"""
        current_time = time.time()
        meet_time_interval = (
            current_time - self._last_flush_time >= self._config.flush_interval
        )
        if meet_time_interval:
            logging.debug(f"meet time interval {self._config.flush_interval}")
        meet_batch_size = self._queue.qsize() >= self._config.batch_size
        if meet_batch_size:
            logging.debug(f"meet batch size {self._config.batch_size}")
        return meet_time_interval or meet_batch_size

    def put(self, item: Any) -> None:
        """添加单条数据到缓冲器"""
        with self._lock:
            # 若队列满了，先触发一次刷新（避免阻塞）
            if self._queue.full():
                self.flush()
            self._queue.put(item)

        # 检查是否达到批量阈值，达到则触发刷新
        if self.need_flush():
            self.flush()

    def start(self) -> None:
        """启动缓冲器（开启定时刷新线程）"""
        if self._is_running:
            return
        self._is_running = True
        self._last_flush_time = time.time()

    @abstractmethod
    def stop(self) -> None:
        """停止缓冲器（强制刷新剩余数据并关闭线程）"""
        self._is_running = False

    @abstractmethod
    def flush(self, **kwargs):
        pass

    def _flush_loop(self, **kwargs) -> None:
        """定时刷新循环（后台线程）"""
        pass


class SyncWriteBuffer(WriteBuffer[T]):
    """
    同步写操作缓冲器
    """

    def __init__(self, config: WriteBufferConfig, **kwargs):
        super().__init__(config, **kwargs)
        self._queue = self._config.get_queue(mode="sync")
        self._lock = threading.Lock()

    def start(self):
        super().start()
        t = threading.Thread(target=self._flush_loop, daemon=True)
        t.start()
        return t

    def stop(self) -> None:
        """停止缓冲器（强制刷新剩余数据并关闭线程）"""
        super().stop()
        if self._flush_task:
            self._flush_task.join()
        self.flush()  # 退出前强制刷新剩余数据

    def flush(self, **kwargs) -> None:
        """强制刷新缓冲数据（批量处理）"""
        if self._queue.empty():
            return

        # TODO：这里是一次性取出来，是否可以只取batch_size个且不用加锁
        items: List[Any] = []
        with self._lock:
            while not self._queue.empty():
                try:
                    items.append(self._queue.get_nowait())
                except queue.Empty:
                    break

        # 调用用户自定义的批量处理函数
        if items:
            self._handler(items)
            # 更新刷新时间
            self._last_flush_time = time.time()

    def _flush_loop(self, check_interval=0.1, **kwargs):
        while self._is_running:
            if self.need_flush():
                self.flush()
            time.sleep(check_interval)


class AsyncWriteBuffer(WriteBuffer[T]):
    """
    异步写操作缓冲器
    """

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self._queue = self._config.get_queue(mode="async")
        self._lock = asyncio.Lock()

    async def start(self):
        super().start()
        self._flush_task = asyncio.create_task(self._flush_loop())
        return self._flush_task

    async def stop(self):
        super().stop()
        if self._flush_task:
            await self._flush_task
        await self.flush()

    async def put(self, item: Any):
        async with self._lock:
            if self._queue.full():
                await self.flush()
            await self._queue.put(item)

        if self.need_flush():
            await self.flush()

    async def flush(self, **kwargs):
        if self._queue.empty():
            return

        items: List[Any] = []
        async with self._lock:
            while not self._queue.empty():
                items.append(await self._queue.get())

        if items:
            if inspect.iscoroutinefunction(self._handler):
                await self._handler(items)  # 调用异步批量处理函数
            else:
                self._handler(items)
            self._last_flush_time = time.time()

    async def _flush_loop(self, check_interval=0.1, **kwargs):
        while self._is_running:
            if self.need_flush():
                await self.flush()
            await asyncio.sleep(check_interval)  # 异步休眠
