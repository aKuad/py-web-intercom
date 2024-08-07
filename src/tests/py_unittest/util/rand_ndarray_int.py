# coding: UTF-8
"""Generate a random ``ndarray[int*]``

Author:
  aKuad

"""

import numpy as np


def generate_rand_ndarray_int(shape: tuple[int, int], dtype) -> np.ndarray:
  """Generate a random ``ndarray[int*]``

  Note:
    It's for only int array, not for float array.

  Args:
    shape(tuple[int, int]): Shape of array to generate
    dtype: Type of array

  Returns:
    numpy.ndarray: Generated random array

  """
  return np.random.randint(np.iinfo(dtype).min, np.iinfo(dtype).max, size=shape, dtype=dtype)
