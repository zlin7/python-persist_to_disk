import os
from importlib import reload
import sys
import persist_to_disk
import functools


@persist_to_disk.persist()
def test_func(a=1):
    print('test_func', a)
    return a


@functools.lru_cache()
def test_func2(a=1):
    print(a)
    return a


@persist_to_disk.persist()
def test_func3(b: int, a: int = 1, *, c=3, **kwargs) -> int:
    print(a, b)
    return test_func(b)
    return a


@persist_to_disk.persist()
def test_func4(b: int, a: int = 1, **kwargs) -> int:
    print(a, b)
    return a


if __name__ == '__main__':
    # test_func()
    # test_func2()
    test_func3(3)
    test_func4(3)
