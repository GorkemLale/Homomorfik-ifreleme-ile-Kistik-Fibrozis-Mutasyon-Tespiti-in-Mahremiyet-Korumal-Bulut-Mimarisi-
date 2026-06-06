from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os

class get_pybind_include(object):
    def __str__(self):
        import pybind11
        return pybind11.get_include()

seal_dir = os.path.abspath(os.path.join("deps", "SEAL"))
seal_include = os.path.join(seal_dir, "native", "src")
seal_build_include = os.path.join(seal_dir, "build", "native", "src")
seal_lib_dir = os.path.join(seal_dir, "build", "lib")

ext_modules = [
    Extension(
        "seal_cpp",
        ["seal_cpp_binding.cpp"],
        include_dirs=[
            get_pybind_include(),
            seal_include,
            seal_build_include
        ],
        library_dirs=[seal_lib_dir],
        libraries=["seal-4.1"],
        language="c++",
        extra_compile_args=["-std=c++17", "-O3"]
    ),
]

setup(
    name="seal_cpp",
    version="1.0.0",
    ext_modules=ext_modules,
)
