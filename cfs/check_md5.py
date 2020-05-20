
from os.path import join, dirname, exists
from io import BytesIO
import hashlib

import pandas as pd
from terminaltables import AsciiTable

from .resources import root_dir


def pandas_to_ascii(df):

    def convert(v):
        if isinstance(v, float):
            return ('%.2f' % v).replace('+', '')
        else:
            return str(v)

    idxname = df.index.name or ','.join(df.index.names)
    colname = df.columns.name or ','.join(df.columns.names)

    T = [[idxname + "/" + colname] + list(df.columns)]
    for idx, cols in df.iterrows():
        T = T + [[str(idx)] + [convert(v) for v in cols]]
    tab = AsciiTable(T)
    tab.outer_border = False
    return tab.table.replace('+', '|')


def md5sum(byts):
    f = BytesIO(byts)
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: f.read(4096), b''):
        hash_md5.update(chunk)

    return hash_md5.hexdigest()


def _check_md5(f):
    filename = join(root_dir, f.name)
    if not exists(filename):
        return 'NA'
    md5_onrecord = f[0]
    with open(filename, 'rb') as f:
        md5_computed = md5sum(f.read())
    if md5_onrecord == md5_computed:
        return 'valid'
    else:
        return 'invalid'


def check_md5():
    filename = join(dirname(__file__), "md5sums.txt")
    assert exists(filename), f"md5sums not found ({filename})"
    df = pd.read_csv(filename, sep='  ', index_col=1, header=None,
                     engine='python')
    df.index.name = 'filename'
    df.columns = ['md5sum']

    def _check(f):
        filename = join(root_dir, f.name)
        if not exists(filename):
            return 'NA'

        with open(filename, 'rb') as fp:
            md5_computed = md5sum(fp.read())

        return 'valid' if f.md5sum == md5_computed else 'invalid'

    df['status'] = df.apply(_check, axis=1)
    df.columns.name = "field"
    df.sort_values('status', inplace=True)
    print(pandas_to_ascii(df))
    print('------------------------------------------')
    for status in ('valid', 'invalid', 'NA'):
        n = sum(df.status == status)
        print(f">>> {n} files are '{status}'")

    print('------------------------------------------')
    return 0 if all(df.status == 'valid') else 1
