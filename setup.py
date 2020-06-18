from setuptools import setup, find_packages
from Savetube.version import __version__
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = "Savetube",
    version = __version__,
    author = "bawaviki",
    author_email = "bawaviki99@gmail.com",
    description = ("Youtube-dl GUI Wrapper"),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license = "MIT",
    python_requires='>=3',
    keywords = ['savetube', 'youtube-dl-gui', 'SavTube', 'Savetube', 'youtube-dl GUI'],
    url = "http://github.com/bawaviki/savetube",
    download_url = "https://github.com/bawaviki/savetube/archive/v_{}.tar.gz".format(__version__),
    package_dir={'Savetube' : 'Savetube'},
    packages=find_packages(),
    scripts=['savetube.py'],
    package_data = {
    'Savetube.GUI': ['*']
    },
    install_requires=[
        'youtube-dl',
        'pyfiglet',
        'termcolor'
    ],
    entry_points ={
        'console_scripts' : ['savetube = Savetube.__main__:main']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
