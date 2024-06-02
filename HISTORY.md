## 0.0.7
==================
1. Shared cache vs local cache (the latter specified by `persist_path_local` in the config). This assumes local reads faster. Can be skipped
2. Add support for `argparse.Namespace` to support a common practice.
3. Add support for argument `alt_dirs` for `persistf`.
    For example, if the function is called `func1` and its default cache path is `/path/repo-2/module/func1`, and we have cache from a similar code base at a different location, whose cache looks like `/path/repo-1/module/func1`.
    Then, we could do:
    ```
    @ptd.persistf(alt_dirs=["/path/repo-1/module/func1"])
    def func1(a=1):
        print(1)
    ```
    A call to `func1` will read cache from `repo-1` and write it to `repo-2`.
4. Add support for argument `alt_root` for `manual_cache`. It could be a function that modifies the default path.

## 0.0.6
==================
1. Added the json serialization mode. This could be specified by `hash_method` when calling `persistf`.
2. If a function is specified to be `cache=ptd.READONLY`, no file lock will be used (to avoid unncessary conflict).

## 0.0.5
==================
1. `lock_granularity` can be set differently for each function.
2. Changed the default cache folder to `.cache/persist_to_disk`.

## 0.0.4
==================
1. Changed the behavior of `switch_kwarg`. Now, this is not considered an input to the wrapped function. For example, the correct usage is
    ```
    @ptd.persistf(switch_kwarg='switch')
    def func1(a=1):
        print(1)
    func1(a=1, switch=ptd.NOCACHE)
    ```
    Note how `switch` is not an argument of `func1`.
2. Fix the path inference step, which now finds the absolute paths for `project_path` or `file_path` (the path to the file contaning the function) before inferencing the structure.

## 0.0.3
==================

1. Added `set_project_path` to config.