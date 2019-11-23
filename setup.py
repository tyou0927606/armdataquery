from setuptools import setup, find_packages

setup(
    name='armdata',
    description='Demo a CLI query implementation and testing',
    
    version='1.0',
    author='Tim You',
    author_email='you_tianxiang@yahoo.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    install_requires=['pytest', 'click', 'td-client', 'tabulate', 'mock'],
    entry_points={
        'console_scripts': ['query = armdata.query_cli:start']
    }
)