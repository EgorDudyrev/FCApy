import setuptools


def run_install(**kwargs):
    with open("README.md", "r") as fh:
        long_description = fh.read()

    extras_require = {
        'context': [
            'pandas'
        ],
        'mvcontext': [
            'frozendict'
        ],
        'lattice': [
            'tqdm'
        ],
        'algorithms': [
            'joblib',
            'scikit-learn',
            'tqdm',
        ],
        'visualizer': [
            'matplotlib',
            'networkx>=2.5',
            'plotly',
        ],
        'tests': [
            'scikit-learn'
        ],
        'docs': [
            'numpydoc',
            'sphinx_rtd_theme',
            'sphinx',
            'nbsphinx',
        ]
    }
    extras_require['all'] = list(set(i for val in extras_require.values() for i in val))

    setuptools.setup(
        name="fcapy",
        version="0.1.0",
        author="Egor Dudyrev",
        author_email="egor.dudyrev@yandex.ru",
        description="A library to work with formal (and pattern) contexts, concepts, lattices",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/EgorDudyrev/FCApy",
        packages=setuptools.find_packages(exclude=("tests",)),
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
        extras_require=extras_require
    )


if __name__ == "__main__":
    run_install()
