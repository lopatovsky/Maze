from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name='maze',
    version='0.2',
    description='generate and solve maze',
    author='Lukas Lopatovsky',
    author_email='lopatovsky@gmail.com',
    license='Public Domain',
    url='https://github.com/lopatovsky/Maze',
    py_modules=['maze'],
    ext_modules=cythonize('maze/maze_solver.pyx', language_level=3, include_dirs=[numpy.get_include()]),
    include_dirs=[numpy.get_include()],
    install_requires=[
        'Cython',
        'NumPy',
    ],
)
