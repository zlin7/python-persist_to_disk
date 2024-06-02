"""Main functions for persist_to_disk."""

import inspect
import os
from typing import Any, Callable, List, Optional, Tuple, Union

from . import persister
from .config import Config
from .persister import (
    CACHE,
    CHECKONLY,
    NOCACHE,
    READONLY,
    RECACHE,
    Persister,
    persist_func_version,
)

# Global config so user could set the root directory for persist ops
config = Config()


def persistf(
    freq=None,
    hashsize: int = None,
    skip_kwargs: List[str] = None,
    expand_dict_kwargs: Union[List[str], str] = None,
    groupby: List[str] = None,
    switch_kwarg: str = "cache_switch",
    cache: int = None,
    lock_granularity: str = None,
    hash_method="pickle",
    local: bool = False,
    alt_dirs: List[str] = None,
):
    """Base decorator that does all the heavy-lifting for caching, taking additional arguments.

    Args:
        freq (_type_, optional): unused for now. Defaults to None.
        hashsize (int, optional): Calls/Inputs to func are hashed into *hashsize* buckets.
            Defaults to what's set in config.
        skip_kwargs (List[str], optional): these kwargs are ignored (e.g. gpu_id, verbose, ...).
            Defaults to empty list.
        expand_dict_kwargs (Union[List[str], str], optional): arguments to expand.
            Applies to arguments to *func* that are dictionaries.
            If str, it must be `all` which means all dictionaries are recursively expanded.
            Note that any calls with un-expanded dictionary arguments will fail.
            Defaults to None.
        groupby (List[str], optional): Create several levels of cache.
            For example, if groupby=['dataset'], then calls with each
            dataset will be stored in a separate folder.
            Defaults to None.
        switch_kwarg (str, optional):
            A switch to turn on/off the caching mechanism.
            Takes value in {NOCACHE, CACHE, RECACHE, READONLY}
            Defaults to 'cache_switch'.
        cache (int, optional):
            Same as switch_kwarg but this is a function-level setting (not call level).
            Useful for recaching/debugging purposes.
            Defaults to None (equivalent to CACHE).
        lock_granularity (str, optional):
            Granularity of the lock. Can be either 'function', 'call' or 'global'.
        hash_method (str, optional):
            Method to hash the inputs. Can be either 'pickle' or 'json'.
            Defaults to 'pickle'.
        local (bool, optional):
            Whether to use local cache. Defaults to False.
        alt_dirs (List[str], optional):
            Alternative directories to *read* the cache. Defaults to None.
    """

    def _decorator(func):
        return persist_func_version(
            func,
            config,
            freq=freq,
            hashsize=hashsize,
            skip_kwargs=skip_kwargs,
            expand_dict_kwargs=expand_dict_kwargs,
            groupby=groupby,
            switch_kwarg=switch_kwarg,
            cache=cache,
            lock_granularity=lock_granularity,
            hash_method=hash_method,
            local=local,
            alt_dirs=alt_dirs,
        )

    return _decorator


def clear_locks(clear=False):
    """This function clears ALL locks for your project, if any.
    Such locks could be created in multi-process usage of persist_to_disk.
    Please only use it when you are sure no process is still using these locks to access files.

    Args:
        clear (bool, optional):
            If clear=False, only prints the dead locks.
            If True, actually delete them.
            Defaults to False.
    """
    for root, dirs, files in os.walk(config.get_project_persist_path(), topdown=False):
        for name in files:
            if name.endswith(".lock"):
                print(os.path.join(root, name))
                if clear:
                    os.remove(os.path.join(root, name))
        continue
        for name in dirs:
            print(os.path.join(root, name))


def get_caller_cache_path(make_if_necessary=True):
    """infer the cache path for the caller, for manual cache.

    Args:
        make_if_necessary (bool, optional):
            Make the directory if it does not exist.
            Defaults to True.

    Returns:
        str: default path to save the cache
    """
    return persister._get_caller_cache_path(
        config, inspect.stack()[1], make_if_necessary
    )


def manual_cache(
    key: str,
    obj: Any = None,
    write: bool = False,
    checkonly: bool = False,
    local: bool = False,
    stacklevel=1,
    alt_root: Optional[Union[str, Callable]] = None,
) -> Any:
    """Manual cache helper.
    Each function gets a directory to store all results.
    Each result is saved with *key* as the filename.
    If *write*, writes *obj* with key=*key*.

    WARNING: This function is not multiprocess-safe.
        This is because each file should contain only 1 cache result.

    Args:
        key (str):
            key of cache.
        obj (Any, optional):
            Result to cache. Defaults to None.
        write (bool, optional):
            Write or read the cache. Defaults to False.
        checkonly (bool, optional):
            Check if the file exists without reading. Defaults to False.
        local (bool, optional):
            Whether to use local cache. Defaults to False.
        stacklevel (int, optional):
            How many levels to go back to get the caller. Defaults to 1.
        alt_root (Optional[Union[str, Callable]], optional):
            Alternative root to read the cache, or function to mod the cache_dir. Defaults to None.

    Returns:
        Any: cached result when *write*, else None.
    """
    assert not (write and checkonly), "Cannot write and checkonly at the same time."
    flag = RECACHE if write else (CHECKONLY if checkonly else READONLY)
    return persister._manual_cache_infer_path(
        key, obj, flag, config, inspect.stack()[stacklevel], local=local, alt_root=alt_root
    )


__all__ = ["config", "clear_locks", "persistf", "get_caller_cache_path", "manual_cache"]

__version__ = "0.0.7"
__author__ = "Zhen Lin"
__credits__ = ""
