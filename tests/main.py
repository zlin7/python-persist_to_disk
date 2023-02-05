
import os
from importlib import reload
import sys
import persist_to_disk
import functools


@persist_to_disk.persist()
def test_func(a=1):
    print(a)
    return a


@functools.lru_cache()
def test_func2(a=1):
    print(a)
    return a


if __name__ == '__main__':
    test_func()
