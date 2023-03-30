"""This file demonstrates that persist_to_disk is multiprocess-safe.
"""
from multiprocessing import Pool

from persist_to_disk import persistf


@persistf(hashsize=1)
def wait_and_return(a):
    import time
    time.sleep(3)
    print(f"Waited 3 seoncds for input {a}.")
    return a


@persistf(hashsize=1)
def write_big_stuff(a):
    b = (10000 * (a + 1))
    print(f"Generating a big cache with {b}=10000*({a}+1) elements.")
    return [1] * b


if __name__ == '__main__':
    with Pool(10) as p:
        print(p.map(wait_and_return, list(range(10))))
        res = p.map(write_big_stuff, list(range(10)))
        print(list(map(len, res)))
        res = p.map(write_big_stuff, list(range(10)))
        print(list(map(len, res)))
        # write_big_stuff(1)
