from os.path import join
from setuptools import setup

__version__ = ''
exec(open(join('cfs', 'version.py')).read())
requirements = open('requirements.txt').read().split('\n')

setup(
    name='cleveland-family-study',
    version=__version__,
    packages=['cfs'],
    install_requires=requirements,
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
