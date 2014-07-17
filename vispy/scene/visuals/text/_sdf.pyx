

# A Cython implementation of the "eight-points signed sequential Euclidean
# distance transform algorithm" (8SSEDT)

import numpy as np
cimport numpy as np
from libc.math cimport sqrt
cimport cython

__all__ = ['_get_distance_field']

cdef np.complex64_t MAX_VAL = (1e6 + 1e6j)


def _get_sdf(data, spread=25):
    """_get_sdf(data, spread=25)

    Calculate the distance field for a set of data.

    Parameters
    ----------
    data : array-like
        Image data. Should be scaled between 0 and 1.
    spread : int
        Amount of border to add.

    Returns
    -------
    field : array-like
        Array of signed distances (np.float32).
    """
    assert spread > 0 and isinstance(spread, int)
    # add borders to help indexing of _calc_distance_field
    h = data.shape[0] + spread * 2 + 2
    w = data.shape[1] + spread * 2 + 2
    field = np.zeros((h, w), np.float32)
    field[spread+1:spread+1+data.shape[0],
          spread+1:spread+1+data.shape[1]] = data
    _calc_distance_field(field, w, h, spread)
    return np.array(field[1:-1, 1:-1], dtype=np.float32)


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
def _calc_distance_field(np.float32_t [:,:] pixels, int w, int h, np.float32_t sp_f):
    # initialize grids
    cdef np.ndarray[np.complex64_t, ndim=2] g0 = np.zeros((h, w), np.complex64)
    cdef np.ndarray[np.complex64_t, ndim=2] g1 = np.zeros((h, w), np.complex64)
    cdef Py_ssize_t y, x
    for y in range(h):
        g0[y, 0] = MAX_VAL
        g0[y, w-1] = MAX_VAL
        g1[y, 0] = MAX_VAL
        g1[y, w-1] = MAX_VAL
        for x in range(1, w-1):
            if pixels[y, x] > 0:
                g0[y, x] = MAX_VAL
            if pixels[y, x] < 1:
                g1[y, x] = MAX_VAL
    for x in range(w):
        g0[0, x] = MAX_VAL
        g0[h-1, x] = MAX_VAL
        g1[0, x] = MAX_VAL
        g1[h-1, x] = MAX_VAL

    # Propagate grids
    _propagate(g0)
    _propagate(g1)

    # Subtracting and normalizing
    cdef np.float32_t r_sp_f_2 = 1. / (sp_f * 2.)
    for y in range(1, h-1):
        for x in range(1, w-1):
            pixels[y, x] = sqrt(dist(g0[y, x])) - sqrt(dist(g1[y, x]))
            if pixels[y, x] < 0:
                pixels[y, x] = (pixels[y, x] + sp_f) * r_sp_f_2
            else:
                pixels[y, x] = 0.5 + pixels[y, x] * r_sp_f_2
            pixels[y, x] = max(min(pixels[y, x], 1), 0)


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
cdef Py_ssize_t compare(np.complex64_t *cell, np.complex64_t xy, np.float32_t *current):
    cdef np.float32_t val = dist(xy)
    if val < current[0]:
        cell[0] = xy
        current[0] = val


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
cdef np.float32_t dist(np.complex64_t val):
    return val.real*val.real + val.imag*val.imag


@cython.boundscheck(False)  # designed to stay within bounds
@cython.wraparound(False)  # we don't use negative indexing
cdef void _propagate(np.complex64_t [:, :] grid):
    cdef Py_ssize_t height = grid.shape[0]
    cdef Py_ssize_t width = grid.shape[1]
    cdef Py_ssize_t y, x
    cdef np.float32_t current
    cdef np.complex64_t a0=-1, a1=-1j, a2=-1-1j, a3=1-1j
    cdef np.complex64_t b0=1
    cdef np.complex64_t c0=1, c1=1j, c2=-1+1j, c3=1+1j
    cdef np.complex64_t d0=-1
    height -= 1
    width -= 1
    for y in range(1, height):
        for x in range(1, width):
            current = dist(grid[y, x])
            # (-1, +0), (+0, -1), (-1, -1), (+1, -1)
            compare(&grid[y, x], grid[y, x-1] + a0, &current)
            compare(&grid[y, x], grid[y-1, x] + a1, &current)
            compare(&grid[y, x], grid[y-1, x-1] + a2, &current)
            compare(&grid[y, x], grid[y-1, x+1] + a3, &current)
        for x in range(width - 1, 0, -1):
            current = dist(grid[y, x])
            # (+1, +0)
            compare(&grid[y, x], grid[y, x+1] + b0, &current)
    for y in range(height - 1, 0, -1):
        for x in range(width - 1, 0, -1):
            current = dist(grid[y, x])
            # (+1, +0), (+0, +1), (-1, +1), (+1, +1)
            compare(&grid[y, x], grid[y, x+1] + c0, &current)
            compare(&grid[y, x], grid[y+1, x] + c1, &current)
            compare(&grid[y, x], grid[y+1, x-1] + c2, &current)
            compare(&grid[y, x], grid[y+1, x+1] + c3, &current)
        for x in range(1, width):
            current = dist(grid[y, x])
            # (-1, +0)
            compare(&grid[y, x], grid[y, x-1] + d0, &current)
