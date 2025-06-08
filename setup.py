from setuptools import setup, find_packages

setup(
    name='ai_assistant',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'transformers',
        'torch',
    ],
    author='Your Name',
    description='A package to load and run local LLMs using Hugging Face Transformers',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
