import logging
import pickle
from typing import Optional, Mapping, Any

import haiku as hk
import jax
import jax.numpy as jnp
import jax.random as jr
import jax.nn as jnn
import haiku.initializers as hki
import einops
import functools as ft

import numpy as np
import optax
import pandas as pd

def load_dataset(filename='./data/train.csv', filename1='./data/test.csv'):
    train_data = pd.read_csv(filename)
    test = pd.read_csv(filename1).values[:, :]

    train_y = train_data.values[:, 0]
    train_x = train_data.values[:, 1:]

    train_x = (train_x - 128.0) / 255.0
    test = (test - 128.0) / 255.0

    train_x = np.expand_dims(train_x.reshape((-1, 28, 28)), axis=3)
    test = np.expand_dims(test.reshape((-1, 28, 28)), axis=3)

    return jnp.array(train_x), jnp.array(train_y, dtype=jnp.int32), jnp.array(test)
    


x, y, test = load_dataset()

def get_generator_parallel(x, y, rng_key, batch_size, num_devices):
    def batch_generator():
        n = x.shape[0]
        key = rng_key
        kk = batch_size // num_devices
        while True:
            key, k1 = jax.random.split(key)
            perm = jax.random.choice(k1, n, shape=(batch_size,))
            
            yield x[perm, :, :, :].reshape(num_devices, kk, *x.shape[1:]), y[perm].reshape(num_devices, kk, *y.shape[1:])
    return batch_generator()  


