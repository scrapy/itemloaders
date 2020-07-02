from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='itemloaders',
    version='1.0.1',
    url='https://github.com/scrapy/itemloaders',
    project_urls={
        'Documentation': 'https://itemloaders.readthedocs.io/',
        'Source': 'https://github.com/scrapy/itemloaders',
    },
    description="Base library for scrapy's ItemLoader",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Scrapinghub',
    author_email='info@scrapinghub.com',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    python_requires='>=3.5',
    install_requires=[
        # before updating these versions, be sure they are not higher than
        # scrapy's requirements
        'w3lib>=1.17.0',
        'parsel>=1.5.0',
        'jmespath>=0.9.5',
        'itemadapter>=0.1.0',
    ],
    # extras_require=extras_require,
)
