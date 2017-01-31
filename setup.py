# coding=utf-8

"""
Union is an easy to use plug-and-play tool for logs aggregation.
"""

import os
from setuptools import setup, find_packages


def get_version():
    basedir = os.path.dirname(__file__)
    try:
        with open(os.path.join(basedir, 'union/version.py')) as f:
            loc = {}
            exec(f.read(), loc)
            return loc['VERSION']
    except:
        raise RuntimeError('No version info found.')

setup(
    name='union',
    version=get_version(),
    url='https://github.com/sancau/union/',
    license='MIT',
    author='Alexander Tatchin',
    author_email='alexander.tatchin@gmail.com',
    description='Union is an easy to use plug-and-play tool for logs aggregation.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'psycopg2==2.6.2',
        'redis==2.10.5',
        'click==6.7',
        'pyyaml==3.12'
    ],
    entry_points={
        'console_scripts': [
            'union = union.cli:main'
        ],
    },
    classifiers=[
        #  As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
          'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
	'Topic :: Internet :: Log Analysis',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Distributed Computing',
    ]
)
