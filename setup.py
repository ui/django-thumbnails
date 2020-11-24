# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-thumbnails',
    version='0.3.2',
    author='Selwin Ong',
    author_email='selwin.ong@gmail.com',
    packages=['thumbnails'],
    url='https://github.com/ui/django-thumbnails',
    license='MIT',
    description='A simple Django app to manage image/photo thumbnails. Supports remote/cloud storage systems like Amazon S3.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README.rst']},
    install_requires=['django', 'da-vinci', 'shortuuid'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
