
# Installation

`pip install .`

**By default, a folder called `.persist_to_disk` is created under your home directory, and will be used to store cache files.**
If you want to change it, see "Global Settings" below.

# Global Settings

To set global settings (for example, where the cache should go by default), please do the following:

```
import persist_to_disk as ptd
ptd.config.generate_config()
```
Then, you could (optionally) change the settings in the generated `config.ini`:

1. `persist_path`: where to store the cache.
    All projects you have on this machine will have a folder under `persist_path` by default, unless you specify it within the project (See examples below).
2. `hashsize`: How many hash buckets to use to store each function's outputs. Default=500.
3. `lock_granularity`:
    How granular the lock is.
    This could be `call`, `func` or `global`.

    * `call` means each hash bucket will have one lock, so only only processes trying to write/read to/from the same hash bucket will share the same lock.
    * `func` means each function will have one lock, so if you have many processes calling the same function they will all be using the same lock.
    * `global` all processes share the same lock (I tested that it's OK to have nested mechanism on Unix).


# Quick Start

### Basic Example
Using `persist_to_disk` is very easy.
For example, if you want to write a general training function:
```
import torch 

@ptd.persistf()
def train_a_model(dataset, model_cls, lr, epochs, device='cpu'):
    ...
    return trained_model_or_key

if __name__ == '__main__':
    train_a_model('MNIST', torch.nn.Linear, 1e-3, 30)
```

Suppose the above is in a file with path `~/project_name/pipeline/train.py`. 
If we are in `~/project_name` and run `python -m pipeline.train`, a cache folder will be created under `PERSIST_PATH`, like the following:
```
PERSIST_PATH(=ptd.config.get_persist_path())
├── project_name-[autoid]
│   ├── pipeline
│   │   ├── train
│   │   │   ├── train_a_model
│   │   │   │   ├──[hashed_bucket].pkl
```
Note that in the above, `[autoid]` is a auto-generated id. 
`[hashed_bucket]` will be an int in [0, `hashsize`).

### Multiprocessing
Note that `ptd.persistf` can be used with [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) directly.


# Advanced Settings

## `config.set_project_path` and `config.set_persist_path`

There are two important paths for each workspace/project: `project_path` and `persist_path`. 
You could set them by calling `ptd.config.set_project_path` and `ptd.config.set_persist_path`.

On a high level, `persist_path` determines *where* the results are cached/persisted, and `project_path` determines the structure of the cache file tree.
Following the basic example, `ptd.config.persist_path(PERSIST_PATH)` will only change the root directory. 
On the other hand, supppose we add a line of `ptd.config.set_project_path("./pipeline")` to `train.py` and run it again, the new file structure will be created under `PERSIST_PATH`, like the following:
```
PERSIST_PATH(=ptd.config.get_persist_path())
├── pipeline-[autoid]
│   ├── train
│   │   ├── train_a_model
│   │   │   ├──[hashed_bucket].pkl
```

Alternatively, it is also possible that we store some notebooks under `~/project_name/notebook/`. 
In this case, we could set the `project_path` back to `~/project_name`.
You could check the mapping from projects to autoids in `~/.persist_to_disk/project_to_pids.txt`.



## Additional Parameters
`persist` take additional arguments.
For example, consider the new function below:
```
@ptd.persistf(groupby=['dataset', 'epochs'], expand_dict_kwargs=['model_kwargs'], skip_kwargs=['device'])
def train_a_model(dataset, model_cls, model_kwargs, lr, epochs, device='cpu'):
    model = model_cls(**model_kwargs)
    model.to(device)
    ... # train the model
    model.save(path)
    return path
```
The kwargs we passed to `persistf` has the following effects:

* `groupby`: We will create more intermediate directories basing on what's in `groupby`. 
In the example above, the new cache structure will look like
```
PERSIST_PATH(=ptd.config.get_persist_path())
├── project_name-[autoid]
│   ├── pipeline
│   │   ├── train
│   │   │   ├── train_a_model
│   │   │   │   ├── MNIST
│   │   │   │   │   ├── 20
│   │   │   │   │   │   ├──[hashed_bucket].pkl
│   │   │   │   │   ├── 10
│   │   │   │   │   │   ├──[hashed_bucket].pkl
│   │   │   │   ├── CIFAR10
│   │   │   │   │   ├── 30
│   │   │   │   │   │   ├──[hashed_bucket].pkl
```

* `expand_dict_kwargs`: This simply allows the dictionary to be passed in.
This is because we cannot hash a dictionary directly, so there are additionally preprocessing steps for these arguments within `ptd`. 
Note that you can also set `expand_dict_kwargs='all'` to avoid specifying individual dictionary arguements.
However, please only do so IF YOU KNOW what you are passing in - a very big nested dictionary can make the cache-retrievement very slow and use a lot of disk space unnecessarily.

* `skip_kwargs`: This specifies arguments that will be *ignored*. 
For examplte, if we call `train_a_model(..., device='cpu')` and `train_a_model(..., device='cuda:0')`, the second run will simply read the cache, as `device` is ignored. 

### Other useful parameters:
* `hash_size`: Defaults to 500. 
If a function has a lot of cache files, you can also increase this if necessary to reduce the number of `.pkl` files on disk.