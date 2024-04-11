## 0.0.7
==================
1. Shared cache vs local cache (the latter specified by `persist_path_local` in the config). This assumes local reads faster. Can be skipped
2. Add support for `argparse.Namespace` to support a common practice.

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