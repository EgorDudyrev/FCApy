import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fcapy",
    version="0.0.5",
    author="Egor Dudyrev",
    author_email="egor.dudyrev@yandex.ru",
    description="A library to work with formal (and pattern) contexts, concepts, lattices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EgorDudyrev/FCApy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
