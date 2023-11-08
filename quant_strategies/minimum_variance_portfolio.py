import cvxpy as cp
import pandas as pd


class Strategy:
    def __init__(self):
        self.covariance_matrix = None
        self.name = "Minimum Variance"

    def train(self, training_data):
        self.covariance_matrix = training_data.cov()

    def execute(self, returns, min_weight=0.05):
        n_assets = returns.shape[1]

        # Define variables for the portfolio weights
        weights = cp.Variable(n_assets)

        # Define the objective function to minimize portfolio variance
        portfolio_variance = cp.quad_form(weights, self.covariance_matrix)

        constraints = [
            cp.sum(weights) == 1,  # Weights must sum to 1 (fully invested)
            weights >= min_weight,
        ]  # Weights must be non-negative

        # Define the problem as a quadratic optimization problem
        objective = cp.Minimize(portfolio_variance)
        problem = cp.Problem(objective, constraints)

        # Solve the problem
        problem.solve()
        if problem.status == cp.OPTIMAL:
            optimal_weights = weights.value
            optimal_weights = pd.DataFrame(optimal_weights, index=returns.columns).transpose()
            optimal_weights = optimal_weights.loc[optimal_weights.index.repeat(returns.shape[0] - 1)].reset_index(drop=True)
            optimal_weights = optimal_weights.set_index(returns.index[1:])
            return optimal_weights
        else:
            raise Exception("Optimization failed")
