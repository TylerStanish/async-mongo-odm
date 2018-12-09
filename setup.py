from setuptools import setup

setup(
    name='odm',
    version='0.1.0-alpha',
    packages=['odm', 'odm.meta', 'odm.type', 'odm.document'],
    url='',
    license='MIT',
    author='tylerstanish',
    author_email='tystanish@gmail.com',
    description='A lightweight async MongoDB ODM',
    install_requires=[
        'motor'
    ]
)
