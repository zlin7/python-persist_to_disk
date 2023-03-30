"""Examples of using the manual cache functionality.

This is useful when you want to specify your own key.
The persist_to_disk module will still infer the cache path for you.
"""

import time

import persist_to_disk as ptd


def _test_func_worker(a):
    for _ in range(100):
        a += 1
    print("The computation actually happened here.")
    time.sleep(2)
    return a

def test_func(a=1, debug=False):
    key = str(a)
    result = ptd.manual_cache(key)
    if result is None:
        # do something
        result = _test_func_worker(a)
        ptd.manual_cache(key, result, write=not debug)
    return result


class Tester:
    def __init__(self, a=1, debug=False) -> None:
        # We can also do something similar
        print(f"Cache within this function will be stored in {ptd.get_caller_cache_path()}")

        key = str(a)
        self.result = ptd.manual_cache(key)
        if self.result is None:
            self.result = _test_func_worker(a)
            ptd.manual_cache(key, self.result, write=not debug)


if __name__ == '__main__':
    test_func()
    Tester()
