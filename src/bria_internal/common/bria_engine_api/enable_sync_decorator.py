import asyncio
import functools
from typing import Awaitable, Callable, ParamSpec, TypeVar

from bria_internal.common.bria_engine_api import running_in_async_context

P = ParamSpec("P")
T = TypeVar("T")


def enable_run_synchronously(func: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """
    Decorator that enables execution of an async function in a sync context (synchronously).

    This decorator allows async functions to be called from both sync and async contexts:
    - If called from an async context: returns the coroutine (awaitable)
    - If called from a sync context: automatically runs the coroutine in a
    new event loop which will block the thread (will execute synchronously).

    Args:
        func: The async function to decorate

    Returns:
        A function that can be called from both sync and async contexts
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        if running_in_async_context():
            # Already in async context, return the coroutine
            return func(*args, **kwargs)
        else:
            # Not in async context, run in new event loop
            return asyncio.run(func(*args, **kwargs))

    return wrapper


def enable_run_synchronously_method(func: Callable[P, Awaitable[T]]) -> Callable[P, T]:
    """
    Decorator for async methods that automatically executes
    within an asyncio event loop if not already in an async context.

    Similar to `enable_run_synchronously` but designed for class methods.

    Args:
        func: The async method to decorate

    Returns:
        A method that can be called from both sync and async contexts
    """

    @functools.wraps(func)
    def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> T:
        if running_in_async_context():
            # Already in async context, return the coroutine
            return func(self, *args, **kwargs)
        else:
            # Not in async context, run in new event loop
            return asyncio.run(func(self, *args, **kwargs))

    return wrapper
