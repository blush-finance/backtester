import math
import datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def download_equity_returns(ticker_symbols, days):
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=days)
    equity_data = pd.DataFrame()

    for ticker_symbol in ticker_symbols:
        equity = yf.Ticker(ticker_symbol)

        # Download historical prices
        price_data = equity.history(period="1d", start=start_date, end=end_date)

        close_prices = price_data.filter(like="Close")
        close_prices.columns = [ticker_symbol for col in close_prices.columns]

        if equity_data.empty:
            equity_data = close_prices
        else:
            equity_data = equity_data.join(close_prices, how="outer")

    equity_returns = equity_data.pct_change().iloc[1:]
    equity_returns.index = equity_returns.index.date

    return equity_returns


class Report:
    def __init__(self, strategy_name, portfolio_weights, portfolio_returns, stock_return_data):
        self.strategy_name = strategy_name
        self.portfolio_weights = portfolio_weights
        self.asset_values = pd.DataFrame()
        self.portfolio_returns = portfolio_returns
        self.portfolio_volatility = (portfolio_returns.std() * 100 * math.sqrt(250))[0]
        self.portfolio_value = 100
        self.portfolio_value_breakdown = self.portfolio_weights.iloc[[0]] * 100 
        self.portfolio_values = pd.Series(name=f"{strategy_name} portfolio values", dtype="object")
        
        for date in portfolio_returns.index:
            portfolio_return = portfolio_returns.loc[date][0]
            self.portfolio_value = self.portfolio_value * (1 + portfolio_return)
            self.portfolio_values = pd.concat([self.portfolio_values, pd.Series({date: self.portfolio_value})])
        
        last_date = None
        for date in stock_return_data.index[1:]:
            if last_date is None:
                last_date = date
                continue

            last_stock_values = self.portfolio_value_breakdown.loc[last_date]
            current_day_returns = stock_return_data.loc[date]
            current_day_stock_values = last_stock_values * (1 + current_day_returns)
            current_day_stock_values.name = date
            current_day_stock_rebalance = self.portfolio_weights.loc[date] * self.portfolio_values[date]
            current_day_stock_rebalance.name = date
            current_day_stock_rebalance = pd.DataFrame(current_day_stock_rebalance).transpose()
            self.portfolio_value_breakdown = pd.concat([self.portfolio_value_breakdown, current_day_stock_rebalance])
        
        self.portfolio_return = self.portfolio_value - 100
        self.sharpe_ratio = (self.portfolio_return - 5) / self.portfolio_volatility
            
            
    def plot_portfolio_returns(self):
        self.portfolio_returns.mul(100).round(2).plot(title=f"{self.strategy_name} portfolio returns", figsize=(18,8), legend=False)
        plt.xlabel(None)
        plt.ylabel("Percentage")
    
    def plot_portfolio_value(self):
        self.portfolio_values.plot(title=f"{self.strategy_name} portfolio value", figsize=(18,8))
    
    def plot_portfolio_value_breakdown(self):
        self.portfolio_value_breakdown.plot(title=f"{self.strategy_name} portfolio value breakdown", figsize=(18,8))
    
    def portfolio_metrics(self):
        return pd.DataFrame([[self.portfolio_return], [self.portfolio_volatility], [self.sharpe_ratio]], columns=["Metric"], index=["Portfolio return", "Portfolio volatility", "Sharpe ratio"]).round(2)
    
    
def display_as_percentage(df):
    return df.mul(100).round(2).astype(str).add(' %')
        
        