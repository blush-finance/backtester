import sys
import argparse
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import skops.io as sio


class Strategy:
    def __init__(self):
        self.models = {}
        self.name = "Random Forest"

    def train(self, X, y):
        stock_names = y.columns
        for stock in stock_names:
            X_train = X.values.reshape(-1, 1)
            y_train = y[stock].values

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)

            self.models[stock] = model

        sio.dump(self.models, "store/random-forest-strategy.sio")

    def execute(self, feature_df, min_weight=0.2):
        self.models = sio.load("store/random-forest-strategy.sio")
        predicted_returns = {}

        for stock, model in self.models.items():
            X = feature_df.values.reshape(-1, 1)

            y_pred = model.predict(X)
            predicted_returns[stock] = y_pred

        predicted_returns = pd.DataFrame(predicted_returns)

        total_predicted_returns = predicted_returns.sum(axis=1)

        # Calculate weights proportional to predicted returns
        weights = predicted_returns.divide(total_predicted_returns, axis=0)

        # Ensure that the minimum weight is satisfied
        min_weight_df = pd.DataFrame(
            np.full(weights.shape, min_weight), columns=weights.columns
        )
        weights = weights.clip(lower=min_weight_df)

        # Normalize weights to ensure they sum up to 1
        weights = weights.divide(weights.sum(axis=1), axis=0)
        weights = weights.set_index(feature_df.index).iloc[1:]

        return weights


parser = argparse.ArgumentParser(
    prog="Random Forest Strategy",
    description="Execute the Random Forest Strategy",
)

parser.add_argument("-e", "--execute", action="store_true")
parser.add_argument("-t", "--train", action="store_true")
parser.add_argument("-X", "--feature", help="feature dataset")
parser.add_argument("-y", "--prediction-target", help="prediction target dataset")

args = parser.parse_args()

feature_dataset = pd.read_csv(args.feature.strip()).set_index("Date")

prediction_target_dataset = None
if args.prediction_target:
    prediction_target_dataset = pd.read_csv(args.prediction_target)

strategy = Strategy()
if args.train:
    strategy.train(feature_dataset, prediction_target_dataset)
elif args.execute:
    weights = strategy.execute(feature_dataset)
    print(weights)
