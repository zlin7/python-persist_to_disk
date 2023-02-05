""" Util functions
"""
import pickle
import os

from .myfilelock import FileLock

PICKLE_PROTOCOL = 4


def dump(obj, file, **kwargs):
    """like pickle.dump but fix a default protocol for compatibility.
    """
    kwargs.setdefault('protocol', PICKLE_PROTOCOL)
    return pickle.dump(obj, file, **kwargs)


def to_pickle(obj, filepath, **kwargs):
    """Like to_pickle in pandas, but avoids pandas dependency.
    """
    with open(filepath, 'wb') as fout:
        dump(obj, fout, **kwargs)


def read_pickle(filepath, **kwargs):
    """Like read_pickle in pandas, but avoids pandas dependency.
    """
    with open(filepath, 'rb') as fin:
        return pickle.load(fin, **kwargs)


def make_dir_if_necessary(dirname, max_depth=3):
    """Check if a directory exists. If not make it with lock.
    Will create nested directories (up to depth=max_depth).

    Args:
        dirname (_type_):
            Target directory.
        max_depth (int, optional):
            Maximum depth for nested creation.
            Defaults to 3.
    """
    if os.path.isdir(dirname):
        return
    assert max_depth >= 0, "Cannot make too many nested directories. Something could be wrong!"
    if not os.path.isdir(os.path.dirname(dirname)):
        make_dir_if_necessary(os.path.dirname(dirname), max_depth - 1)
    fl = FileLock(dirname)
    with fl:
        print(f"{dirname} does not exist. Creating it for persist_to_disk")
        os.makedirs(dirname)
    return


def retrieve_id(meta_file, key, sep='||'):
    """An internal helper to retrieve a mapped id (and create one if necessary).
    """
    with FileLock(meta_file):
        curr_dict, lines = dict(), []
        if os.path.isfile(meta_file):
            with open(meta_file, 'r', encoding='utf-8') as fin:
                lines = fin.readlines()
                curr_dict = dict([line.strip().split(sep) for line in lines])
        if key not in curr_dict:
            curr_dict[key] = pid = str(len(curr_dict)+1)
            with open(meta_file, 'a', encoding='utf-8') as fout:
                fout.write(f"{key}{sep}{pid}\n")
    return curr_dict[key]
