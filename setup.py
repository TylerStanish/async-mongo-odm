from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='odm',
    long_description=long_description,
    version='0.1.0-alpha',
    packages=[find_packages()],
    url='',
    license='MIT',
    author='tylerstanish',
    author_email='tystanish@gmail.com',
    description='A lightweight async MongoDB ODM',
    install_requires=[
        'motor'
    ]
)
