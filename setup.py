from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    name='maze',
    version='0.4',
    description='generate & solve maze, GUI application',
    author='Lukas Lopatovsky',
    author_email='lopatovsky@gmail.com',
    license='GPL',
    url='https://github.com/lopatovsky/Maze',
    py_modules=['maze'],
    ext_modules=cythonize('maze/*.pyx', language_level=3, include_dirs=[numpy.get_include()]),
    include_dirs=[numpy.get_include()],
    install_requires=[
        'Cython',
        'NumPy',
    ],
)
