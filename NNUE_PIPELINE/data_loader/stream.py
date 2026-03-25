'''
import ctypes

from ._native import c_lib, SparseBatchPtr, FenBatchPtr
from .config import CDataloaderSkipConfig, DataloaderSkipConfig


def _to_c_str_array(str_list):
    c_str_array = (ctypes.c_char_p * len(str_list))()
    c_str_array[:] = [s.encode("utf-8") for s in str_list]
    return c_str_array


def create_fen_batch_stream(
    concurrency,
    filenames: list[str],
    batch_size,
    cyclic,
    config: DataloaderSkipConfig,
) -> ctypes.c_void_p:
    return c_lib.dll.create_fen_batch_stream(
        concurrency,
        len(filenames),
        _to_c_str_array(filenames),
        batch_size,
        cyclic,
        CDataloaderSkipConfig(config),
    )


def destroy_fen_batch_stream(stream: ctypes.c_void_p):
    c_lib.dll.destroy_fen_batch_stream(stream)


def fetch_next_fen_batch(stream: ctypes.c_void_p) -> FenBatchPtr:
    return c_lib.dll.fetch_next_fen_batch(stream)


def destroy_fen_batch(fen_batch: FenBatchPtr):
    c_lib.dll.destroy_fen_batch(fen_batch)


def create_sparse_batch_stream(
    feature_set: str,
    concurrency,
    filenames: list[str],
    batch_size,
    cyclic,
    config: DataloaderSkipConfig,
) -> ctypes.c_void_p:
    return c_lib.dll.create_sparse_batch_stream(
        feature_set,
        concurrency,
        len(filenames),
        _to_c_str_array(filenames),
        batch_size,
        cyclic,
        CDataloaderSkipConfig(config),
    )


def destroy_sparse_batch_stream(stream: ctypes.c_void_p):
    c_lib.dll.destroy_sparse_batch_stream(stream)


def get_sparse_batch_from_fens(
    feature_set: str, fens, scores, plies, results
) -> SparseBatchPtr:
    assert len(fens) == len(scores) == len(plies) == len(results)

    def to_c_int_array(data):
        return (ctypes.c_int * len(data))(*data)

    return c_lib.dll.get_sparse_batch_from_fens(
        feature_set.encode("utf-8"),
        len(fens),
        _to_c_str_array(fens),
        to_c_int_array(scores),
        to_c_int_array(plies),
        to_c_int_array(results),
    )


def fetch_next_sparse_batch(stream: ctypes.c_void_p) -> SparseBatchPtr:
    return c_lib.dll.fetch_next_sparse_batch(stream)


def destroy_sparse_batch(batch: SparseBatchPtr):
    c_lib.dll.destroy_sparse_batch(batch)
'''


import ctypes
from ._native import c_lib, IS_NATIVE, SparseBatchPtr, FenBatchPtr
from .config import CDataloaderSkipConfig, DataloaderSkipConfig
from .stream_python import (
    create_sparse_batch_stream as py_create_sparse_batch_stream,
    destroy_sparse_batch_stream as py_destroy_sparse_batch_stream,
    fetch_next_sparse_batch as py_fetch_next_sparse_batch,
)

def _to_c_str_array(str_list):
    c_str_array = (ctypes.c_char_p * len(str_list))()
    c_str_array[:] = [s.encode("utf-8") for s in str_list]
    return c_str_array

def create_sparse_batch_stream(feature_set: str, concurrency, filenames: list[str], batch_size, cyclic, config: DataloaderSkipConfig) -> ctypes.c_void_p:
    if IS_NATIVE and c_lib is not None:
        return c_lib.dll.create_sparse_batch_stream(
            feature_set.encode("utf-8"), concurrency, len(filenames), _to_c_str_array(filenames),
            batch_size, cyclic, CDataloaderSkipConfig(config),
        )
    return py_create_sparse_batch_stream(feature_set, concurrency, filenames, batch_size, cyclic, config)

def destroy_sparse_batch_stream(stream: ctypes.c_void_p):
    if IS_NATIVE and c_lib is not None:
        return c_lib.dll.destroy_sparse_batch_stream(stream)
    return py_destroy_sparse_batch_stream(stream)

def fetch_next_sparse_batch(stream: ctypes.c_void_p) -> SparseBatchPtr:
    if IS_NATIVE and c_lib is not None:
        return c_lib.dll.fetch_next_sparse_batch(stream)
    ptr = py_fetch_next_sparse_batch(stream)
    if ptr is None:
        return ctypes.cast(0, SparseBatchPtr)  # NULL when exhausted
    return ptr

# FEN-related APIs (not used in your run). Keep guarded stubs:
def create_fen_batch_stream(*args, **kwargs): 
    if IS_NATIVE and c_lib is not None: return c_lib.dll.create_fen_batch_stream(*args, **kwargs)
    raise NotImplementedError
def destroy_fen_batch_stream(*args, **kwargs):
    if IS_NATIVE and c_lib is not None: return c_lib.dll.destroy_fen_batch_stream(*args, **kwargs)
def fetch_next_fen_batch(*args, **kwargs):
    if IS_NATIVE and c_lib is not None: return c_lib.dll.fetch_next_fen_batch(*args, **kwargs)
    raise NotImplementedError
def destroy_fen_batch(*args, **kwargs):
    if IS_NATIVE and c_lib is not None: return c_lib.dll.destroy_fen_batch(*args, **kwargs)

# --- required by data_loader/__init__.py, but not used in your flow ---
def get_sparse_batch_from_fens(feature_set: str, fens, scores, plies, results):
    """
    Only implemented for the native C++ path in this repo. The Python fallback
    doesn't have a FEN->features converter. If your code hits this on the
    fallback, we’ll raise clearly.
    """
    if IS_NATIVE and c_lib is not None:
        def to_c_int_array(data):
            return (ctypes.c_int * len(data))(*data)
        return c_lib.dll.get_sparse_batch_from_fens(
            feature_set.encode("utf-8"),
            len(fens),
            _to_c_str_array(fens),
            to_c_int_array(scores),
            to_c_int_array(plies),
            to_c_int_array(results),
        )
    raise RuntimeError("Python fallback does not implement get_sparse_batch_from_fens")

def destroy_sparse_batch(batch):
    """
    Match the native API: free a SparseBatch when using C++ loader.
    For the Python fallback, we don't need to do anything.
    """
    if IS_NATIVE and c_lib is not None:
        return c_lib.dll.destroy_sparse_batch(batch)
    # Python fallback: no-op, GC handles memory
    return
