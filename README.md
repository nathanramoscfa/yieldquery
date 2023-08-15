# Yield Query

Yield Query is a Python library for retrieving bond ETF yield data from each ETF issuer's website using a collection of 
bots for automated data collection. This data is then processed and stored as a dataframe and CSV file for further 
analysis or usage in portfolio optimization algorithms as an expected return for a given bond ETF.

## Features

- **Automated Data Collection**: Utilizes a collection of bots to retrieve bond ETF yield data from various ETF issuers' 
websites.
- **Data Processing**: Processes the collected data and stores it as a CSV file.
- **Portfolio Optimization Integration**: Allows for the integration of this data into portfolio optimization 
algorithms, providing expected returns for bond ETFs.

## Installation

Clone the repository and navigate into the directory:

```bash
git clone https://github.com/nathanramoscfa/yieldquery.git
cd yieldquery
```
Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage
### Retrieving Bond ETF Yield Data
To retrieve bond ETF yield data, run the following command from the root directory:

```bash
python main.py
```

This will run the collection of bots and store the data as a CSV file in the `data` directory.

You can also run each bot individually by running the Jupyter Notebook file for each bot in the `dev` directory. 
This will allow you to see the data as it is being collected and processed and troubleshoot. Bots may break if the ETF
issuer changes the format of their website. If this happens, please open an issue or submit a pull request. 

## Documentation

Complete documentation is available on [Read the Docs](link-to-your-readthedocs).

## Contributing

If you'd like to contribute to Yield Query, please fork the repository and use a feature branch. Pull requests are 
warmly welcome.

## License

Yield Query is licensed under the [MIT License](https://github.com/nathanramoscfa/etradebot/blob/main/LICENSE).
