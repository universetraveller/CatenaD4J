from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from pathlib import Path
from shutil import which
from os import getcwd
from setup_unix_user import build_toolkit

class Builder(_build_py):

    def run(self):
        d4j_home = Path(which('defects4j')).resolve().parents[2]
        c4j_home = Path(getcwd()).resolve()

        build_toolkit(c4j_home, str(d4j_home)) 

        super().run()

setup(
    name='catena4j',
    version='2.0.0',
    packages=find_packages(),

    include_package_data=True,

    package_data={
        'catena4j': [
            '../projects/**/*', 
            '../resources/*',
            '../toolkit/target/toolkit.jar',
        ],
    },

    entry_points={
        'console_scripts': [
            'catena4j=catena4j.bootstrap:system',
        ],
    },

    cmdclass={
        'build_py': Builder,  # Override build_py command to include JAR build
    },

    install_requires=[
    ],

    # metadata
    author='universetraveller',
    description='Python library and script for CatenaD4J',
    url='https://github.com/universetraveller/CatenaD4J'
)