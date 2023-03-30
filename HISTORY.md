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