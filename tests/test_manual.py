import os
from importlib import reload
import sys
import persist_to_disk
import functools


def test_func(a=1):
    key = str(a)
    if persist_to_disk.manual_cache(key) is None:
        print(a)
        persist_to_disk.manual_cache(key, a, write=True)
    return persist_to_disk.manual_cache(key)


class Tester:
    def __init__(self) -> None:
        print(persist_to_disk.get_caller_cache_path())


if __name__ == '__main__':
    test_func()
    Tester()
