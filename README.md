# Backtester

## Introduction

This repo demonstrates how to create an investment strategy agnostic backtester.

In the Jupyter Notebook you can see two examples: a classical quant strategy and a machine learning strategy, both using the backtester.

## Usage

### Jupyter notebook

You can run the Jupyter notebook (`main.ipynb`) to get an idea what we are building.

### Server

To use the Go server to execute one of the strategies in python run inside the server folder: `go run . <path to strategy folder> <path to dataset>`

We only started working on the server. It is a work in progress.

## Strategies as Python packages

Strategies can be uploaded to our server as a python package.

Here an example of a strategy's structure:

- `README.md`
- `LICENSE`
- `requirements.txt`
- `setup.py`
- `__init__.py`
- `__main__.py`
- `<strategy name>` (either a file or a module)

We will need a `requirements.txt` file to install the needed dependencies of the strategy.

Most importantly a strategy is expected to accept a path to a dataset in CSV format with the flag `-d` or `--dataset` and to print a set of weights in CSV format.

## Next steps

- Move the backtester to a server
- Allow a user to upload an investment strategy as a file
- Annualize returns, sharpe ratio etc.
- Implement rebalance frequencies for the backtester
