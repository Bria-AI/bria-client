import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar


def running_in_async_context() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


P = ParamSpec("P")
T = TypeVar("T")


def enable_run_synchronously(func: Callable[P, Awaitable[T]]) -> Callable[P, T | Awaitable[T]]:
    """
    Decorator that enables execution of an async function in a sync context (synchronously).

    This decorator allows async functions to be called from both sync and async contexts:
    - If called from an async context: returns the coroutine (awaitable)
    - If called from a sync context: automatically runs the coroutine in a
    new event loop which will block the thread (will execute synchronously).

    Args:
        `func: Callable[P, Awaitable[T]]` - The async function to decorate

    Returns:
        `Callable[P, T | Awaitable[T]]` - A function that can be called from both sync and async contexts
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[T] | T:
        if running_in_async_context():
            # Already in async context, return the coroutine
            return func(*args, **kwargs)

        # Not in async context, run in new event loop
        return asyncio.run(func(*args, **kwargs))

    return wrapper
