from filelock import Timeout, FileLock as RawFileLock
assert Timeout is not None


class FileLock(object):
    """A wrapper for filelock.FileLock
    """

    def __init__(self, protected_file_path, timeout=5):
        """ Prepare the file locker. Specify the file to lock and optionally
                the maximum timeout and the delay between each attempt to lock.
        """
        self.lock_path = protected_file_path + ".lock"
        self.lock = RawFileLock(self.lock_path, timeout=timeout)

    def __enter__(self):
        return self.lock.__enter__()

    def __exit__(self, *args, **kwargs):
        return self.lock.__exit__(*args, **kwargs)

    def __del__(self):
        return self.lock.__del__()
