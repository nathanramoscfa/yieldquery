.. yieldquery documentation master file, created by
   sphinx-quickstart on Mon Aug 14 19:06:16 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##########
YieldQuery
##########

YieldQuery is a Python library for retrieving bond ETF yield data from each ETF issuer's website using a collection of
bots for automated data collection. This data is then processed and stored as a dataframe and CSV file for further
analysis or usage in portfolio optimization algorithms as an expected return for a given bond ETF.

Features
========

- Retrieve bond ETF yield data from each ETF issuer's website using a collection of bots for automated data collection
- Process and store data as a dataframe and CSV file for further analysis or usage in portfolio optimization algorithms

Installation
============

Clone the repository and navigate to the directory:

.. code-block:: bash

    git clone https://github.com/nathanramoscfa/yieldquery.git
    cd yieldquery

Install the required dependencies:

.. code-block:: bash

    pip install -r requirements.txt

Usage
=====
Retrieving Bond ETF Yield Data
------------------------------

To retrieve bond ETF yield data, run the following command from the root directory:

.. code-block:: bash

    python main.py

This will run the YieldQuery bots to retrieve bond ETF yield data from each ETF issuer's website. The data will be
processed and stored as a dataframe and CSV file for further analysis or usage in portfolio optimization algorithms.
You can also run the bots individually by running the Jupyter Notebook file for each bot in the 'dev' directory. This
will allow you to see the data as it is being collected and processed. The bots may break if the ETF issuer changes the
format of their website. If this happens, please open an issue or submit a pull request.

Documentation
=============

The full documentation is at https://yieldquery.readthedocs.io/en/latest/index.html#.

Contributing
============

If you'd like to contribute to YieldQuery, please fork the repository and use a feature branch. Pull requests are
warmly welcome.

License
=======

Distributed under the MIT License.

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
