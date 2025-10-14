from setuputil import *
import setuptools

setuptools.setup(
    name=projectname,
    version=version,
    author="k. goger",
    author_email=f"k.r.goger+{projectname}@gmail.com",
    url=f"https://github.com/kr-g/{projectname}",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=python_requires,
    install_requires=install_requires,
    entry_points=entry_points,
)

# !!!
# python3 patch_version.py
# !!!

# python3 -m setup sdist build bdist_wheel

# test.pypi
# python3 -m twine upload --repository testpypi dist/*
# python3 -m pip install --index-url https://test.pypi.org/simple/ gitonic --extra-index-url https://pypi.org/simple/
# python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gitonic

# pypi
# python3 -m twine upload dist/*
