
from os import environ as env

root_dir_key = "CFSROOTDIR"

assert root_dir_key in env, f"""
Add path to cfs dataset as an environment variable:
$ export {root_dir_key}=/path/to/cfs/dataset
"""
root_dir = env[root_dir_key]
