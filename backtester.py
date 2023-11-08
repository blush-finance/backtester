import pandas as pd
import numpy as np
from helpers import Report

def test_strategy(
    strategy, strategy_data, stock_return_data, portfolio_value=100
):
    testing_data_returns = np.zeros(len(stock_return_data) - 1)

    weights = strategy.execute(strategy_data)
    for i in range(0, len(stock_return_data) - 1):
        testing_data_returns[i] = np.sum(weights.iloc[i] * stock_return_data.iloc[i])

    testing_data_returns = pd.Series(testing_data_returns, name=f"{strategy.name} returns", index=stock_return_data.index[1:])
    return Report(strategy.name, weights, testing_data_returns, stock_return_data)

