"""Main functions for persist_to_disk.
"""
import os
from .config import Config
from .persister import Persister, NOCACHE, CACHE, RECACHE, READONLY
from .persister import persist_func_version


# Global config so user could set the root directory for persist ops
config = Config()


def persistf(**kwargs):
    """Base decorator that does all the heavy-lifting for caching, taking additional arguments.

    Args:
        func (Callable): The function to cache
        config (Config): The (default) configs that apply to all functions in this project.
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
            Defaults to 'cache'.
        cache (int, optional):
            Same as switch_kwarg but this is a function-level setting (not call level).
            Useful for recaching/debugging purposes.
            Defaults to None (equivalent to CACHE).
    """
    def _decorator(func):
        return persist_func_version(func, config, **kwargs)
    return _decorator


def persist(**kwargs):
    """Base decorator that does all the heavy-lifting for caching, taking additional arguments.

    Args:
        func (Callable): The function to cache
        config (Config): The (default) configs that apply to all functions in this project.
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
            Defaults to 'cache'.
        cache (int, optional):
            Same as switch_kwarg but this is a function-level setting (not call level).
            Useful for recaching/debugging purposes.
            Defaults to None (equivalent to CACHE).
    """
    return lambda func: Persister(func, config, **kwargs)


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
    for root, dirs, files in os.walk(config.get_persist_path(), topdown=False):
        for name in files:
            if name.endswith(".lock"):
                print(os.path.join(root, name))
                if clear:
                    os.remove(os.path.join(root, name))
        continue
        for name in dirs:
            print(os.path.join(root, name))


__all__ = [
    'config',
    'persist',
    'clear_locks',
    'persistf',
]

__version__ = "0.0.1"
__author__ = 'Zhen Lin'
__credits__ = ''
