""" Main script.
"""
from typing import Callable, Optional, List, Tuple, Union
import os
#import time
#import sys
import glob
import copy
import pickle
import hashlib
import inspect
import functools

import six

from .config import Config
from .myfilelock import FileLock, Timeout
from . import _utils
_DEBUG = False
NOCACHE, CACHE, RECACHE, READONLY = [0, 1, 2, 3]


def _print(*args, **kwargs):
    if _DEBUG:
        print(*args, **kwargs)


def get_persist_dir_from_paths(base_dir: str, file_path: str, project_path: str):
    """Infers the directory to store all cache data, basing on the project_path,
     file_path (which should be inside project_path) and the base cache directory base_dir.

    Args:
        base_dir (str): Directory for all cache for project_path.
        file_path (str): The path to the .py file we are interested in.
        project_path (str): Where the project lives (i.e. what os.getcwd() returns).

    Returns:
        str: The directory to store cache for functions in file_path.
    """
    file_path = os.path.normpath(file_path)
    assert file_path.endswith(".py")
    file_path = os.path.splitext(file_path)[0]

    if project_path is None:
        base_dir = os.path.join(base_dir, '.hashed')
        _utils.make_dir_if_necessary(base_dir)
        meta_file = os.path.join(base_dir, 'mapping.txt')
        pid = _utils.retrieve_id(meta_file, file_path, sep='||')
        persist_dir = os.path.join(
            base_dir, f"{os.path.basename(file_path)}-{pid}")
    else:
        project_path = os.path.normpath(project_path)
        assert project_path in file_path, \
            f"Expect file_path to be a sub-directory of project_path,'\
            ' but got {file_path} and {project_path}"
        persist_dir = file_path.replace(
            project_path, os.path.normpath(base_dir))
    return os.path.normpath(persist_dir)


def _hash(k):
    return int(hashlib.md5(pickle.dumps(k, protocol=3)).hexdigest(), 16)


def _persist_rw_curr_results(cache_path, write_key=None, write_val=None):
    fl = FileLock(cache_path)
    with fl:
        try:
            res = _utils.read_pickle(cache_path)
        except Exception as err:
            if os.path.exists(cache_path):
                print(f"Error: {err}. Re-creating a new cache")
            res = {}
            _utils.to_pickle(res, cache_path)
        if write_key is not None:
            res[write_key] = write_val
            _utils.to_pickle(res, cache_path)
        return res


def _persist_write(cache_path, key, func, args, kwargs, alt_roots):
    if alt_roots is not None:
        # try to look up in alterantive root cache paths..
        # If can't find anything, then save to the original path.
        # This is like merging cache.
        # assert _PERSIST_PATH in cache_path, "How did you generate this cache path??"
        raise NotImplementedError()  # Should probably replace before passing in alt_roots
    else:
        val = func(*args, **kwargs)
    try:
        _persist_rw_curr_results(cache_path, key, val)
    except Timeout as err:
        raise err
    return val


def _persist_write_if_necessary(cache_path, key, func, args, kwargs,
                                readonly=False, alt_roots=None):
    try:
        _print(
            f"persist_to_disk: {cache_path} exists? : {os.path.isfile(cache_path)}.")
        res = _persist_rw_curr_results(cache_path)
        _print(
            f"persist_to_disk: Looking up {key} in {cache_path}({res.keys()}): {key in res}.")
        if key in res:
            return res[key]
    except Timeout as err:
        raise err
    assert not readonly, "In readonly mode, but there is no existing cache."
    return _persist_write(cache_path, key, func, args, kwargs, alt_roots=alt_roots)


# test input d={"model": {"1": {"2": 3, '2a': 4}}, 'a': 2}
def _expand_dict_recursive(d):
    old_d = d
    d = {}
    for k, v in old_d.items():
        if isinstance(v, dict):
            v = _expand_dict_recursive(v)
            for kk, vv in v.items():
                d[f"{k}|{kk}"] = vv
        else:
            d[k] = v
    return d


def _get_full_kwargs_noargs(func, args1, kwargs1):
    args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations = inspect.getfullargspec(
        func)
    assert varargs is None, "Does not support functions with *args."
    full_kwargs = {}
    # default values
    if kwonlydefaults is not None:
        full_kwargs.update(kwonlydefaults)
    if defaults is not None:
        full_kwargs.update(dict(zip(args[-len(defaults):], defaults)))
    # input values
    for argi, argv in enumerate(args1):
        full_kwargs[args[argi]] = argv
    full_kwargs.update(kwargs1)
    return full_kwargs


def _clean_kwargs(full_kwargs, skip_kwargs, expand_dict_kwargs):
    for k in skip_kwargs:
        full_kwargs.pop(k, None)
    if isinstance(expand_dict_kwargs, str) and expand_dict_kwargs == 'all':
        full_kwargs = _expand_dict_recursive(full_kwargs.copy())
    else:
        for k in expand_dict_kwargs:
            if k in full_kwargs.keys():
                d = full_kwargs.pop(k)
                full_kwargs.update({f"{k}|{kk}": v for kk, v in d.items()})
    return full_kwargs


def _get_hashed_path_and_key(cache_dir, full_kwargs, hashsize, groupby):
    for k in groupby:
        if isinstance(k, tuple):
            dirname = "$$".join([str(full_kwargs.pop(kk)) for kk in k])
        else:
            dirname = str(full_kwargs.pop(k))
        cache_dir = os.path.join(cache_dir, dirname)
    _utils.make_dir_if_necessary(cache_dir)
    key = tuple(sorted(six.iteritems(full_kwargs), key=lambda x: x[0]))
    hashed_path = os.path.join(cache_dir, f"{_hash(key) % hashsize}.pkl")
    return hashed_path, key


class Persister():
    """Base class that does all the heavy-lifting.
    """

    @classmethod
    def _check_arguments(cls, config: Config, freq, skip_kwargs, hashsize, switch_kwarg,
                         expand_dict_kwargs, groupby, cache):
        special_kwargs = set(groupby + expand_dict_kwargs + skip_kwargs)
        assert len(special_kwargs) == len(groupby) + \
            len(expand_dict_kwargs) + len(skip_kwargs)
        assert switch_kwarg not in special_kwargs

    def __init__(self, func: Callable, config: Config,
                 freq=None, hashsize: int = None,
                 skip_kwargs: List[str] = None, expand_dict_kwargs: Union[List[str], str] = None,
                 groupby: List[str] = None,
                 switch_kwarg: str = 'cache', cache: int = None):
        functools.update_wrapper(self, func)
        self.__defaults__ = six.get_function_defaults(func)
        if skip_kwargs is None:
            skip_kwargs = []
        if expand_dict_kwargs is None:
            expand_dict_kwargs = []
        if groupby is None:
            groupby = []

        Persister._check_arguments(
            config, None, skip_kwargs, hashsize, switch_kwarg, expand_dict_kwargs, groupby, cache)

        assert inspect.getfullargspec(
            func)[1] is None, "Does not support functions with *args."
        # self.__dict__.update(func.__dict__)
        # infodict = get_info(func)

        # workspace config
        self.config = config

        # current function settings
        self.hashsize = hashsize or config.get_hashsize()
        self.freq = freq
        self.skip_kwargs = skip_kwargs
        self.switch_kwarg = switch_kwarg  # 0 is not cache, 1 is cache, 2 is recache
        self.expand_dict_kwargs = expand_dict_kwargs
        self.groupby = groupby

        # Get the cache_dir straight
        self.cache_dir = get_persist_dir_from_paths(
            config.get_persist_path(),
            inspect.getsourcefile(func),
            config.get_project_path()
        )
        self.cache_dir = os.path.join(self.cache_dir, self.__name__)
        assert '__main__' not in self.cache_dir
        _utils.make_dir_if_necessary(self.cache_dir)
        assert freq is None, "Not implemented yet"
        self.alt_roots = config.get_alternative_roots()

        self.cache = cache

    def __call__(self, *args, **kwargs):
        kwargs = copy.deepcopy(kwargs)
        curr_cache_switch = int(kwargs.pop(self.switch_kwarg, CACHE))
        full_kwargs = _get_full_kwargs_noargs(self.__wrapped__, args, kwargs)
        cache_switch = self.cache if self.cache is not None else curr_cache_switch
        if cache_switch == NOCACHE:
            return self.__wrapped__(**full_kwargs)
        _cleaned = _clean_kwargs(
            full_kwargs, self.skip_kwargs, self.expand_dict_kwargs)
        hashed_path, key = _get_hashed_path_and_key(
            self.cache_dir, _cleaned, self.hashsize, self.groupby)
        if cache_switch == RECACHE:
            return _persist_write(hashed_path, key, self.__wrapped__, args, kwargs, alt_roots=None)
        return _persist_write_if_necessary(hashed_path, key, self.__wrapped__, args, kwargs,
                                           readonly=cache_switch == READONLY,
                                           alt_roots=self.alt_roots)

    def clear(self):
        """clean all the cache for self.__wrapped__
        """
        files = glob.glob(f'{self.cache_dir}/*')
        for f in files:
            os.remove(f)


# function version =====================
def persist_func_version(func, config: Config, **kwargs):
    """wrapper so that the func-to-persist can be pickled (e.g. in multiprocessing)
    """
    obj = Persister(func, config, **kwargs)

    @functools.wraps(func)
    def inner(*args, **kwargs):
        return obj(*args, **kwargs)
    return inner
