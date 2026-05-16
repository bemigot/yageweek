# pixi run -e aap python lib-map.py

import numpy as np
import psutil


NEEDLES = ('blas', 'lapack', 'mkl')


def find_math_libs(needles: tuple[str, ...] = NEEDLES) -> list[str]:
    """Return unique BLAS/LAPACK/MKL shared libs mapped into this process after a NumPy matmul."""
    _ = np.random.randn(500, 500) @ np.random.randn(500, 500)  # force BLAS/MKL load
    maps = psutil.Process().memory_maps()
    libs = {m.path for m in maps if any(n in m.path.lower() for n in needles)}
    return sorted(libs)


if __name__ == '__main__':
    print(*find_math_libs(), sep='\n')
