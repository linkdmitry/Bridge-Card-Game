from setuptools import setup, find_packages

setup(
    name='card-game',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple card game project with GUI using Pygame',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pygame>=2.0.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)