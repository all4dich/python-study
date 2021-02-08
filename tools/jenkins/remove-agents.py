import pandas as pd
import argparse
import requests

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--username", required=True)
arg_parser.add_argument("--password", required=True)
arg_parser.add_argument("--url", required=True)
arg_parser.add_argument("--file-path", required=True)
args = arg_parser.parse_args()

df = pd.read_excel(args.file_path)
for idx in df.index:
    ip = df.loc[idx]['IP']
    host = df.loc[idx]['Hostname'].lower()
    delete_url = f"{args.url}computer/{host}/doDelete"
    r = delete_req = requests.post(delete_url, auth=(args.username, args.password))
    print(host, r.status_code)
