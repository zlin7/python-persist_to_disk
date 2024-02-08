import functools

import persist_to_disk as ptd


# The usage is very similar to functools.lru_cache but it saves the results to disk.
@ptd.persistf(local=True)
def test_func(a=1):
    print('test_func', a)
    return a


@functools.lru_cache()
def test_func2(a=1):
    print(a)
    return a


class FakeModel:
    def __init__(self, **kwargs):
        pass
    def to(self, device):
        print(f"Moving model to {device}.")
    def save(self, path):
        print(f"Saving model to {path}.")
    def train(self, lr, echo=30):
        print(f"Training model with lr={lr} for {echo} epochs.")

@ptd.persistf(groupby=['dataset', 'epochs'], expand_dict_kwargs=['model_kwargs'], skip_kwargs=['device'], switch_kwarg='cache')
def train_a_model(dataset, model_cls, model_kwargs, lr, epochs=30, device='cpu',**kwargs):
    # This function demos how to use persist_to_disk in training the model
    model = model_cls(**model_kwargs)
    model.to(device)

    # train the model...

    path  = f"models/{dataset}/{model_cls.__name__}_{epochs}.pt"
    model.train(lr, epochs)

    model.save(path)
    return path


if __name__ == '__main__':

    # By default, we train a model like the following.
    print("\n\nBy default, we train a model like the following. (There is printing only in the first call.)")
    train_a_model('MNIST', FakeModel, {}, lr=0.001)

    # The next call will not actually run the function.
    print("\n\nThe next call will not actually run the function.")
    train_a_model('MNIST', FakeModel, {}, lr=0.001)

    # If we change the lr, the function will be called again.
    print("\n\nIf we change the lr, the function will be called again.")
    train_a_model('MNIST', FakeModel, {}, lr=0.002)

    # Because skip_kwargs=['device'], this argument does not matter
    print("\n\nBecause skip_kwargs=['device'], this argument does not matter")
    train_a_model('MNIST', FakeModel, {}, lr=0.001, device='cuda:0')


    print("\n\nIf we use cache=ptd.NOCACHE, the caching mechanism will be disabled. That is, no writing, no reading.")
    train_a_model('MNIST', FakeModel, {}, lr=0.001, cache=ptd.NOCACHE)

    print("\n\nIf we use cache=ptd.READONLY, we will triger an exception if the cache is not found.")
    try:
        train_a_model('MNIST', FakeModel, {}, lr=0.01, cache=ptd.READONLY)
    except Exception as e:
        print(f"Error: {e}")

    print("\n\nIf we use cache=ptd.RECACHE, the cache will be overwritten")
    train_a_model('MNIST', FakeModel, {}, lr=0.001, cache=ptd.RECACHE)

    test_func(1)