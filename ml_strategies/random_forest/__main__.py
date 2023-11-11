import sys
import argparse
import pandas as pd
import strategy


parser = argparse.ArgumentParser(
    prog="Random Forest Investment Strategy",
    description="Package to execute a minimum variance portfolio investment strategy",
)
parser.add_argument("-d", "--dataset", help="dataset to execute the strategy on")
args = parser.parse_args()

if not args.dataset:
    print("You need to include a path to the feature data", file=sys.stderr)
    sys.exit(1)

dataset_df = pd.read_csv(args.dataset.strip()).set_index("Date")
weights = strategy.execute(dataset_df)

print(weights.to_csv())
sys.exit(0)
