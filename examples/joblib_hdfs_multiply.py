"""Example showing how to use joblib-hadoop with an HDFS store"""

import numpy as np
from joblib import Memory
from joblibhadoop.hdfs import register_hdfs_store_backend

if __name__ == '__main__':
    register_hdfs_store_backend()

    mem = Memory(location='joblib_cache_hdfs', backend='hdfs',
                 verbose=100, compress=True,
                 store_options=dict(host='namenode', port=9000, user='test'))
    mem.clear()
    multiply = mem.cache(np.multiply)
    array1 = np.arange(1000)
    array2 = np.arange(1000)

    print("# First call")
    _ = multiply(array1, array2)

    print("# Second call")
    # Second call should return the cached result
    result = multiply(array1, array2)

    print(result)
