import math
import datetime
import yfinance as yf
import pandas as pd


def data_download(equity_symbols):
    # Define the date range for the last 10 years
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365 * 7)

    # Create an empty DataFrame to store the historical data
    data = pd.DataFrame()

    # Download historical prices for each equity
    for symbol in equity_symbols:
        equity = yf.Ticker(symbol)

        # Download historical prices
        price_data = equity.history(period="1d", start=start_date, end=end_date)

        # Rename the columns to include the stock symbol
        price_data.columns = [f"{symbol}_{col}" for col in price_data.columns]

        # Join the data with the main DataFrame
        if data.empty:
            data = price_data
        else:
            data = data.join(price_data, how="outer")

    # Select only the columns ending with "_Close"
    selected_columns = data.filter(
        like="_Close"
    )  # Selecting columns ending with "_Close"

    close_prices = data.filter(like="_Close")  # Selecting columns ending with "_Close"
    returns = close_prices.pct_change().iloc[1:]

    return returns


class Report:
    def __init__(self, strategy_name, portfolio_weights, portfolio_returns, stock_return_data):
        self.strategy_name = strategy_name
        self.portfolio_weights = portfolio_weights
        self.asset_values = pd.DataFrame()
        self.portfolio_returns = portfolio_returns
        self.portfolio_volatility = portfolio_returns.std() * 100 * math.sqrt(250)
        self.portfolio_value = 100
        self.stocks_values = self.portfolio_weights.iloc[[0]] * 100 
        self.portfolio_values = pd.Series(name=f"{strategy_name} portfolio values", dtype="object")
        
        for date, portfolio_return in portfolio_returns.items():
            self.portfolio_value = self.portfolio_value * (1 + portfolio_return)
            self.portfolio_values = pd.concat([self.portfolio_values, pd.Series({date: self.portfolio_value})])
        
        last_date = None
        for date in stock_return_data.index[1:]:
            if last_date is None:
                last_date = date
                continue

            last_stock_values = self.stocks_values.loc[last_date]
            current_day_returns = stock_return_data.loc[date]
            current_day_stock_values = last_stock_values * (1 + current_day_returns)
            current_day_stock_values.name = date
            current_day_stock_rebalance = self.portfolio_weights.loc[date] * self.portfolio_values[date]
            current_day_stock_rebalance.name = date
            current_day_stock_rebalance = pd.DataFrame(current_day_stock_rebalance).transpose()
            self.stocks_values = pd.concat([self.stocks_values, current_day_stock_rebalance])
            
            
    def plot_portfolio_returns(self):
        self.portfolio_returns.plot(title=f"{self.strategy_name} returns")
    
    def plot_portfolio_value(self):
        self.portfolio_values.plot(title=f"{self.strategy_name} value")
    
    def plot_asset_values(self):
        self.stocks_values.plot(title=f"{self.strategy_name} stock values", figsize=(18,10))
        
        