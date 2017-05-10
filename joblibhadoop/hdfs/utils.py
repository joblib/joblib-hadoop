"""Helpers for easy registration of joblib store backends."""

from joblib import register_store_backend
from .backend import HDFSStoreBackend


def register_hdfs_store_backend():
    """Register a HDFS store backend for joblib memory caching."""
    register_store_backend('hdfs', HDFSStoreBackend)
