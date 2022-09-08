from setuptools import setup, find_packages

setup(
    name='object_storage',
    version='1.0',
    description='Simple Object Storage api',
    author='Bianca Petrut',
    #author_email='gward@python.net',
    #url='https://www.python.org/sigs/distutils-sig/',
    packages=find_packages(),
    install_requires=[
        'toml',
        'Flask',
        'SQLAlchemy',
        'Flask-SQLAlchemy',
        'flask-json-schema',
        'flask-expects-json',
        'six'
    ],
    entry_points={
        'console_scripts': [
            'object_storage_api = object_storage.cmd.api:main',
        ]
    }
)