import yfinance as yf
import pandas as pd
import numpy as np
import cvxpy as cp
import Strategies
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ML Strategy Function
def train_ml_strategy(training_data):
    models = {}
    
    stock_names = training_data.columns[:training_data.shape[1]-1]
    for stock in stock_names:
        X_train = training_data['^GSPC_Close'].values.reshape(-1, 1) #s&p 500 as a feature
        y_train = training_data[stock].values

        # Initialize and train the Random Forest model
        rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_model.fit(X_train, y_train)

        # Store the model in the dictionary
        models[stock] = rf_model

    return models

#Weight calculator based on predicted returns for the ML Strategy
def calculate_proportional_weights(predicted_returns, min_weight=0.05):
    # Ensure that the predicted_returns is a DataFrame
    if not isinstance(predicted_returns, pd.DataFrame):
        raise ValueError("Input predicted_returns should be a DataFrame")

    # Calculate total predicted returns for normalization
    total_predicted_returns = predicted_returns.sum(axis=1)

    # Calculate weights proportional to predicted returns
    weights = predicted_returns.divide(total_predicted_returns, axis=0)

    # Ensure that the minimum weight is satisfied
    min_weight_df = pd.DataFrame(np.full(weights.shape, min_weight), columns=weights.columns)
    weights = weights.clip(lower=min_weight_df)

    # Normalize weights to ensure they sum up to 1
    weights = weights.divide(weights.sum(axis=1), axis=0)

    return weights

#Minimum Volatility optimization strategy
def get_minimum_variance_portfolio(expected_returns):

    # Define expected returns 
    # covariance_matrix 
    
    covariance_matrix = expected_returns.cov()
    
    # Number of assets
    n_assets = expected_returns.shape[1]

    # Define variables for the portfolio weights
    weights = cp.Variable(n_assets)

    # Define the objective function to minimize portfolio variance
    portfolio_variance = cp.quad_form(weights, covariance_matrix)

    # Define the constraints
    constraints = [cp.sum(weights) == 1,  # Weights must sum to 1 (fully invested)
                   weights >= 0]           # Weights must be non-negative

    # Define the problem as a quadratic optimization problem
    objective = cp.Minimize(portfolio_variance)
    problem = cp.Problem(objective, constraints)

    # Solve the problem
    problem.solve()
    if problem.status == cp.OPTIMAL:
        optimal_weights = weights.value
        return optimal_weights
    else:
        raise Exception("Optimization failed")
        
        
# Backtesting Function
def backtest_strategy(strategy_type, strategy, returns_data, in_sample_split):
    if strategy_type == "ML" :
        training_data = returns_data[:in_sample_split]
        testing_data = returns_data[in_sample_split:]
        model_precisions = {}
        predicted_returns = {}
        models = strategy(training_data)
        
        testing_data_returns = np.zeros(len(returns_data)-in_sample_split)
        testing_data_volatility = np.zeros(len(returns_data)-in_sample_split)
        
        
        stock_names = returns_data.columns[:returns_data.shape[1]-1]
        for stock in stock_names:
            model = models[stock]
            X_test = testing_data['^GSPC_Close'].values.reshape(-1, 1)
            y_test = testing_data[stock].values

            # Make predictions using the model
            y_pred = model.predict(X_test)

            # Calculate the model's precision (e.g., R-squared)
            r2 = r2_score(y_test, y_pred)

            model_precisions[stock] = r2
            predicted_returns[stock] = y_pred
            
        predicted_returns = pd.DataFrame(predicted_returns)
        weights = Strategies.calculate_proportional_weights(predicted_returns)
        
        portfolio_value = 100
        # Compute return and volatility
        for i in range(0,len(testing_data_returns)-1):
            testing_data_returns[i] = np.sum(weights.iloc[i] * testing_data.iloc[i])
            # testing_data_volatility[i] = np.sqrt(weights.iloc[i].T @ testing_data.cov() @ weights.iloc[i])
            portfolio_value = portfolio_value * (1 + testing_data_returns[i])
        return model_precisions, predicted_returns, weights, testing_data_returns, portfolio_value
    
    elif strategy_type == "Quant" :
        out_of_sample_returns = np.zeros(len(returns_data)-in_sample_split)
        out_of_sample_volatility = np.zeros(len(returns_data)-in_sample_split)
        n_assets = returns_data.shape[1]

        in_sample_data = returns_data[:in_sample_split]
        out_of_sample_data = returns_data[in_sample_split:]
        out_of_sample_len= out_of_sample_data.shape[0]
        
        portfolio_value=100
        j=0
        for i in range(out_of_sample_len, len(returns_data)):
                weights = strategy(returns_data[:i])
                out_of_sample_returns[j] = np.sum(weights * returns_data.iloc[i])
                out_of_sample_volatility[j] = np.sqrt(weights.T @ returns_data[:i].cov() @ weights)
                portfolio_value=portfolio_value*(1+out_of_sample_returns[j])
                j=j+1

        out_of_sample_returns = pd.DataFrame(out_of_sample_returns)
        out_of_sample_volatility = pd.DataFrame(out_of_sample_volatility) 
        return out_of_sample_returns, out_of_sample_volatility, portfolio_value
    
    
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
    selected_columns = data.filter(like='_Close')  # Selecting columns ending with "_Close"

    # Save the selected data to a CSV file
    selected_columns.to_csv("us_equities_close_data.csv")
    
    close_prices = data.filter(like='_Close')  # Selecting columns ending with "_Close"
    # Save the selected data to a CSV file
    close_prices.to_csv("us_equities_close_data.csv")
    returns = close_prices.pct_change().iloc[1:]
    returns.to_csv("us_equities_returns_data.csv")
    
    return returns