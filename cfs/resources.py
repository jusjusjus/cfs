from os import environ as env
from os.path import join, exists

root_dir_key = "CFSROOTDIR"
root_dir = ''
metafile = ''
if env.get('CI') is None:
    assert root_dir_key in env, f"""
    Add path to cfs dataset as an environment variable:
    $ export {root_dir_key}=/path/to/cfs/dataset
    """
    root_dir = env[root_dir_key]
    metafile = join(root_dir, 'datasets', 'cfs-visit5-dataset-0.5.0.csv')
    assert exists(metafile), f"Missing meta-data file: {metafile}"
