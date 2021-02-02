import argparse
import pandas as pd
from datetime import datetime

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--path", required=True)
args = arg_parser.parse_args()

before_read = datetime.now()
df_excel = pd.read_excel(args.path)
after_read = datetime.now()
print(f"Info: time to read {args.path} = {after_read - before_read}")
df_excel.apply("count")
df_excel[['type', 'time_build_sh_in_seconds']].groupby('type').mean()
df = df_excel
a = pd.pivot_table(df, values=['host'], aggfunc="count", index=['branch_name', 'type'], columns=['year', 'month'], fill_value=0)['host']
year_2020 = a[: 'host']