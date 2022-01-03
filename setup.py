# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-thumbnails',
    version='0.7.0',
    author='Selwin Ong',
    author_email='selwin.ong@gmail.com',
    packages=['thumbnails'],
    url='https://github.com/ui/django-thumbnails',
    license='MIT',
    description='A simple Django app to manage image/photo thumbnails. Supports remote/cloud storage systems like Amazon S3.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    include_package_data=True,
    package_data={'': ['README.md']},
    install_requires=['django>=2.0', 'da-vinci', 'shortuuid', 'pillow'],
    extras_require = {
        'redis':  ['redis']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
