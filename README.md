
# Installation

`pip install .`

**By default, a folder called `.persist_to_disk` is created under your home directory, and will be used to store cache files.**
If you want to change it, see "Global Settings" below.

## Global Settings

To set global settings (for example, where the cache should go by default), please do the following:

```
import persist_to_disk as ptd
ptd.config.generate_config()
```
Then, you could change the settings there:

1. `persist_path`: where to store the cache.
    All projects you have on this machine will have a folder under `persist_path` by default, unless you specify it within the project (See examples below).
2. `hashsize`: How many hash buckets to use to store each function's outputs. Default=500.
3. `lock_granularity`:
    How granular the lock is.
    This could be `call`, `func` or `global`.
    `call` means each hash bucket will have one lock, so only only processes trying to write/read to/from the same hash bucket will share the same lock.
    `func` means each function will have one lock, so if you have many processes calling the same function they will all be using the same lock.
    `global` all processes share the same lock (I tested that it's OK to have nested mechanism on Unix).


# Example

Using `persist_to_disk` is very easy.
```
@ptd.persistf()
def train_a_model(dataset, model_cls, lr, epochs):
    ...
    return trained_model_or_key
```

Note that `ptd.persistf` can be used with multiprocessing directly.
If target function (e.g. `train_a_model`) is not gonna be pickled by such pipelines, you could use `persist`:
```
@ptd.persist()
def _train_a_model(dataset, model_cls, lr, epochs):
    ...
    return trained_model_or_key

def train_a_model(*args, **kwargs):
    trained_model_or_key = _train_a_model(*args, **kwargs)
    ... # Do more stuff
    return trained_model_or_key
```
`persist` and `persistf` take the same arguments.
For example, if you want to group the cache folder by dataset (so you can manage them easier manually), and your function takes some dictionary as input (which is not hashable), you could do:
```
@ptd.persistf(groupby=['dataset'], expand_dict_kwargs=['model_kwargs'])
def train_a_model(dataset, model_cls, model_kwargs, lr, epochs):
    ...
```

### Project-specific `persist_path`

You could specify the place to save cache on the fly by:
```
import persist_to_disk as ptd
ptd.config.set_persist_path(YOUR_PATH)
```
Note that you can also `set_hashsize`.
Project-level settings will overwrite the global settings.
Function-level settings (e.g. `hashsize`) will further overwrite project-level settings.
