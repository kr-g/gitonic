import setuptools
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()


def find_version(fnam, version="VERSION"):
    with open(fnam) as f:
        cont = f.read()
    regex = f'{version}\s*=\s*["]([^"]+)["]'
    match = re.search(regex, cont)
    if match is None:
        raise Exception(
            f"version with spec={version} not found, use double quotes for version string"
        )
    return match.group(1)


def find_projectname():
    cwd = os.getcwd()
    name = os.path.basename(cwd)
    return name


file = os.path.join("pygitgrab", "__init__.py")
version = find_version(file)
projectname = find_projectname()

setuptools.setup(
    name=projectname,
    version=version,
    author="k.r. goger",
    author_email=f"k.r.goger+{projectname}@gmail.com",
    description="grab only certain information from remote git repo and store them local",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/kr-g/{projectname}",
    packages=setuptools.find_packages(),
    license="MIT",
    keywords="python utility shell, git",
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)

# python3 -m setup sdist build bdist_wheel
# twine upload dist/*
