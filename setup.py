from setuptools import setup, find_packages

setup(
    name='yieldquery',
    version='0.0.0',
    author='Nathan Ramos, CFA®',
    author_email='nathan.ramos.github@gmail.com',
    description="Yield Query is a Python library for retrieving bond ETF yield data from each ETF issuer's website "
                "using a collection of bots for automated data collection.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nathanramoscfa/yieldquery',
    packages=find_packages(exclude=['*.ipynb_checkpoints', '*.tests', '*.tests.*', 'tests.*', 'tests']),
    install_requires=[
        'beautifulsoup4==4.12.2',
        'numpy==1.23.5',
        'pandas==1.5.3',
        'python-dotenv==1.0.0',
        'requests==2.28.2',
        'selenium==4.9.0',
        'tqdm==4.65.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.11',
)
