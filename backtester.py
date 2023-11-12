import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def run(
    strategy,
    test_data,
    start_date,
    window_size=None,
):
    strategy_data_returns = pd.DataFrame()

    weights = pd.DataFrame()
    for current_date in test_data[start_date:].index:
        data = test_data.loc[:current_date]
        if window_size:
            data = data.iloc[-window_size:]

        # Make sure that only weights for current date are appended to results
        output = strategy.execute(data)
        current_date_weights = output.loc[[current_date]]

        weights = pd.concat([weights, current_date_weights])

    return weights


def analyze(
    strategy_name,
    portfolio_weights,
    stock_returns,
):
    return Report(strategy_name, portfolio_weights, stock_returns)


class Report:
    def __portfolio_value_breakdown(self, portfolio_weights, stock_returns):
        current_portfolio_value = 100
        portfolio_value_breakdown = pd.DataFrame()
        for date in stock_returns.index:
            # Rebalance
            portfolio_value_breakdown = pd.concat(
                [
                    portfolio_value_breakdown,
                    pd.DataFrame(
                        portfolio_weights.loc[[date]] * current_portfolio_value
                    ),
                ]
            )

            # Calculate return
            portfolio_value_breakdown.loc[date] = portfolio_value_breakdown.loc[
                date
            ] * (1 + stock_returns.loc[date])

            current_portfolio_value = portfolio_value_breakdown.loc[date].sum()

        return portfolio_value_breakdown

    def __init__(self, strategy_name, portfolio_weights, stock_returns):
        self.strategy_name = strategy_name
        self.portfolio_weights = portfolio_weights
        self.portfolio_value_breakdown = self.portfolio_value_breakdown(
            portfolio_weights, stock_returns
        )
        self.portfolio_values = pd.DataFrame(
            self.portfolio_value_breakdown.sum(axis=1), columns=["Value"]
        )
        self.portfolio_returns = self.portfolio_values.pct_change().iloc[1:]
        self.portfolio_value = self.portfolio_values.iloc[-1][0]

        self.portfolio_return = self.portfolio_value - 100
        self.portfolio_volatility = (
            self.portfolio_returns.std() * 100 * math.sqrt(250)
        )[0]
        self.sharpe_ratio = (self.portfolio_return - 5) / self.portfolio_volatility

    def plot_portfolio_returns(self):
        self.portfolio_returns.mul(100).round(2).plot(
            title=f"{self.strategy_name} portfolio returns",
            figsize=(18, 8),
            legend=False,
        )
        plt.xlabel(None)
        plt.ylabel("Percentage")

    def plot_portfolio_value(self):
        self.portfolio_values.plot(
            title=f"{self.strategy_name} portfolio value", figsize=(18, 8), legend=False
        )

    def plot_portfolio_value_breakdown(self):
        self.portfolio_value_breakdown.plot(
            title=f"{self.strategy_name} portfolio value breakdown", figsize=(18, 8)
        )

    def portfolio_metrics(self):
        return pd.DataFrame(
            [[self.portfolio_return], [self.portfolio_volatility], [self.sharpe_ratio]],
            columns=["Metric"],
            index=["Portfolio return", "Portfolio volatility", "Sharpe ratio"],
        ).round(2)
