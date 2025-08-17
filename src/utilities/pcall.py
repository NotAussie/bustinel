"""
This module provides a utility function `pcall` for safely invoking asynchronous
coroutines or coroutine functions while handling specified exceptions. It mimics
Lua's `pcall` behaviour by returning a tuple containing the result or exception
and a boolean indicating success.
"""

import inspect
from typing import Awaitable, Callable, Optional, Tuple, Type, TypeVar, Union

T = TypeVar("T")


async def pcall(
    coro: Union[Awaitable[T], Callable[[], Awaitable[T]]],
    handle: Optional[Tuple[Type[BaseException], ...]] = (Exception,),
) -> Tuple[Union[T, BaseException], bool]:
    """
    Asynchronously calls a coroutine or coroutine function and safely catches specified exceptions.

    Mimics Lua's `pcall` behaviour by returning a tuple where the first element
    is either the result or the exception, and the second is a boolean indicating success.

    Args:
        coro (Union[Awaitable[T], Callable[[], Awaitable[T]]]):
            A coroutine object or a zero-argument coroutine function to call.
        handle (Optional[Tuple[Type[BaseException], ...]]):
            A tuple of exception classes to catch. Defaults to (Exception,).

    Returns:
        Tuple[Union[T, BaseException], bool]:
            - If successful: (result, True)
            - If an exception is caught: (exception_instance, False)

    Example:
        async def succeed():
            return 123

        async def fail():
            raise ValueError("fail!")

        await pcall(succeed)              # (123, True)
        await pcall(fail())               # (ValueError(...), False)
        await pcall(fail, (ValueError,))  # (ValueError(...), False)
    """
    try:
        if callable(coro) and inspect.iscoroutinefunction(coro):
            coro = coro()

        if not inspect.isawaitable(coro):
            raise TypeError("Expected an awaitable or a coroutine function.")

        result = await coro
        return result, True
    except handle if handle else (Exception,) as e:
        return e, False
