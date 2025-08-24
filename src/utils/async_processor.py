#!/usr/bin/env python3
"""
Advanced Threading and Async Manager for Telegram Group Inspector
Provides optimized concurrent processing capabilities
"""

import asyncio
import concurrent.futures
import logging
import threading
from functools import wraps
from typing import Any, Callable, List, Optional

logger = logging.getLogger(__name__)


class ThreadPoolManager:
    """Advanced thread pool manager for CPU-intensive tasks"""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize thread pool manager"""
        import os

        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers, thread_name_prefix="TGI_Worker"
        )
        self._shutdown = False

    def submit_task(self, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Submit a task to the thread pool"""
        if self._shutdown:
            raise RuntimeError("ThreadPoolManager has been shut down")
        return self.thread_pool.submit(func, *args, **kwargs)

    async def run_in_thread(self, func: Callable, *args, **kwargs) -> Any:
        """Run a function in a thread and await the result"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)

    def shutdown(self, wait: bool = True):
        """Shutdown the thread pool"""
        self._shutdown = True
        self.thread_pool.shutdown(wait=wait)


class AsyncTaskManager:
    """Manages async tasks with concurrency control"""

    def __init__(self, max_concurrent_tasks: int = 10):
        """Initialize async task manager"""
        self.max_concurrent_tasks = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.active_tasks: List[asyncio.Task] = []

    async def run_concurrent_tasks(
        self, tasks: List[Callable], *args, **kwargs
    ) -> List[Any]:
        """Run multiple tasks concurrently with semaphore control"""

        async def _run_with_semaphore(task):
            async with self.semaphore:
                return await task(*args, **kwargs)

        coroutines = [_run_with_semaphore(task) for task in tasks]
        return await asyncio.gather(*coroutines, return_exceptions=True)

    async def run_with_progress(
        self, tasks: List[Callable], progress_callback: Optional[Callable] = None
    ) -> List[Any]:
        """Run tasks with progress reporting"""
        results = []
        total = len(tasks)

        for i, task in enumerate(tasks):
            async with self.semaphore:
                try:
                    result = await task()
                    results.append(result)
                    if progress_callback:
                        await progress_callback(i + 1, total, result)
                except Exception as e:
                    logger.error(f"Task {i} failed: {e}")
                    results.append(e)
                    if progress_callback:
                        await progress_callback(i + 1, total, e)

        return results


class OptimizedProcessor:
    """Optimized processor combining threading and async capabilities"""

    def __init__(self):
        """Initialize optimized processor"""
        self.thread_manager = ThreadPoolManager()
        self.async_manager = AsyncTaskManager()
        self._lock = threading.Lock()

    async def process_messages_batch(
        self, messages: List, processor_func: Callable, batch_size: int = 100
    ) -> List[Any]:
        """Process messages in optimized batches"""
        if not messages:
            return []

        # Split messages into batches
        batches = [
            messages[i : i + batch_size] for i in range(0, len(messages), batch_size)
        ]

        async def process_batch(batch):
            """Process a single batch"""
            return await self.thread_manager.run_in_thread(processor_func, batch)

        # Process batches concurrently
        batch_tasks = [process_batch(batch) for batch in batches]
        batch_results = await self.async_manager.run_concurrent_tasks(batch_tasks)

        # Flatten results
        results = []
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"Batch processing failed: {batch_result}")
                continue
            if isinstance(batch_result, list):
                results.extend(batch_result)
            else:
                results.append(batch_result)

        return results

    async def download_media_concurrent(
        self, media_items: List, download_func: Callable, max_concurrent: int = 5
    ) -> List[Any]:
        """Download media files concurrently with rate limiting"""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_limit(item):
            async with semaphore:
                try:
                    return await download_func(item)
                except Exception as e:
                    logger.error(f"Media download failed for {item}: {e}")
                    return None

        download_tasks = [download_with_limit(item) for item in media_items]
        return await asyncio.gather(*download_tasks, return_exceptions=True)

    def shutdown(self):
        """Cleanup resources"""
        self.thread_manager.shutdown()


def async_cached(ttl: int = 300):
    """Async cache decorator with TTL"""
    cache = {}
    cache_times = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import time

            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()

            # Check if cached and not expired
            if key in cache and (current_time - cache_times[key]) < ttl:
                return cache[key]

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[key] = result
            cache_times[key] = current_time

            return result

        return wrapper

    return decorator


def rate_limit(calls_per_second: float = 1.0):
    """Rate limiting decorator for async functions"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import time

            current_time = time.time()
            time_since_last = current_time - last_called[0]

            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)

            last_called[0] = time.time()
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Global processor instance
_global_processor: Optional[OptimizedProcessor] = None


def get_processor() -> OptimizedProcessor:
    """Get global processor instance"""
    global _global_processor
    if _global_processor is None:
        _global_processor = OptimizedProcessor()
    return _global_processor


def cleanup_processor():
    """Cleanup global processor"""
    global _global_processor
    if _global_processor:
        _global_processor.shutdown()
        _global_processor = None
