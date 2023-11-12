import datetime
import yfinance as yf
import pandas as pd


def download_equity_returns(ticker_symbols, start_date, end_date):
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
    return equity_returns


def display_as_percentage(df):
    df_copy = df.copy()
    df_copy.index = df_copy.index.date

    return df_copy.mul(100).round(2).astype(str).add(" %")
