from setuptools import setup, find_packages

setup(
    name='itemloaders',
    version='0.1',
    url='---',
    project_urls = {
        'Documentation': '---',
        'Source': '---',
        'Tracker': '---',
    },
    description='---',
    long_description='---',
    author='---',
    maintainer='---',
    maintainer_email='---',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Scrapy',
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
        'w3lib==1.21.0',
        'parsel==1.5.2',
        'jmespath==0.9.5''
    ],
    # extras_require=extras_require,
)
