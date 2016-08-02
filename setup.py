from os.path import join, dirname
from setuptools import setup

with open(join(dirname(__file__), 'requires.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name="fshare",
    version="0.0.1",
    description="file share over http",
    author="guyskk",
    author_email='guyskk@qq.com',
    url="https://github.com/guyskk/fshare",
    license="MIT",
    packages=["fshare"],
    entry_points={
        'console_scripts': ['fshare=fshare.__main__:main'],
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)