from setuptools import setup

import firebase



def readme():
    '''Read README file'''
    with open('README.rst') as infile:
        return infile.read()


setup(
    name='firebase-manager',
    version=firebase.__version__,
    description='Database manager for firebase',
    long_description=readme().strip(),
    author='',
    author_email='',
    url='https://github.com/trycoast/firebase-manager',
    license='MIT',
    packages=['firebase'],
    install_requires=['requests', 'firebase-admin', 'pydantic'],
    keywords=[
        'storage',
        'firebase',
        'firestore',
        'firebase-admin',
        'firebase-manager',
        'database-manager',
    ],
    include_package_data=True,
    zip_safe=False
)
