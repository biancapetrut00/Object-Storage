from setuptools import setup

setup(
    name='object_storage',
    version='1.0',
    description='Simple Object Storage api',
    author='Bianca Petrut',
    #author_email='gward@python.net',
    #url='https://www.python.org/sigs/distutils-sig/',
    packages=['object_storage'],
    install_requires=[
        'toml'
    ],
    entry_points={
        'console_scripts': [
            'object_storage_api = object_storage.cmd.api:main',
        ]
    }
)