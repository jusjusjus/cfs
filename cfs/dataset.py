from typing import List, Union
from os.path import join, exists, dirname, splitext
from functools import cached_property, lru_cache

import pandas as pd
from edfpy import EDF

from .resources import root_dir, metafile
from .profusion import Profusion

cache = lru_cache

SidType = Union[int, str]


class Dataset:

    def __init__(self):
        self.metafile = metafile
        self.md5sums = join(dirname(__file__), "md5sums.txt")

    def __getitem__(self, subject_id: SidType):
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        entry = {
            'edf': self.edf(subject_id),
            'xml': self.xml(subject_id),
            'sid': subject_id
        }
        info = self.subject_info(subject_id, as_dict=True) or {}
        entry.update(**info)
        return entry

    def __len__(self) -> int:
        return len(self.subject_ids)

    @cache
    def edf(self, subject_id: SidType):
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        filename = join(root_dir, self.files.loc[subject_id].filenames.edf)
        return EDF.read_file(filename)

    @cache
    def xml(self, subject_id: SidType) -> pd.DataFrame:
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        filepath = join(root_dir, self.files.loc[subject_id].filenames.xml)
        profusion = Profusion.read(filepath)
        dt = profusion.epoch_length
        labels = profusion.sleep_stages
        t0 = [s * dt for s in range(len(labels))]
        df = pd.DataFrame(data={
            't0': t0, 'dt': dt, 'stage': labels
        })
        df = df[df.stage.apply(lambda x: x is not None)]
        out: pd.DataFrame = df[['t0', 'dt', 'stage']]
        return out

    @cached_property
    def subject_ids(self) -> List[str]:
        return list(map(str, self.files.index))

    def subject_info(self, subject_id: SidType, as_dict: bool = False):
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        info = self._subject_info.loc[subject_id].dropna()
        return info.to_dict() if as_dict else info

    @cached_property
    def _subject_info(self) -> pd.DataFrame:
        df = pd.read_csv(self.metafile)
        assert isinstance(df, pd.DataFrame)
        df['nsrrid'] = df.nsrrid.apply(str)
        df.set_index('nsrrid', inplace=True)
        return df

    @cached_property
    def files(self) -> pd.DataFrame:
        assert exists(self.md5sums), f"md5sums not found ({self.md5sums})"
        df = pd.read_csv(self.md5sums, sep='  ', header=None, engine='python')
        assert isinstance(df, pd.DataFrame)
        df.columns = pd.Index(['md5sum', 'filenames'])
        del df['md5sum']
        df['type'] = df.filenames.apply(
            lambda filename: splitext(filename)[1][1:]
        )
        df = df[(df.type == 'xml') | (df.type == 'edf')]
        i = df.filenames.str.contains('profusion') \
            | df.filenames.str.contains('edfs')
        df = df[i]
        df['sid'] = None
        index = df['type'] == 'edf'
        df['sid'][index] = df.filenames[index].apply(
            lambda filename: splitext(filename)[0].split('-')[-1]
        )
        index = df['type'] == 'xml'
        df['sid'][index] = df.filenames[index].apply(
            lambda filename: filename.split('-')[-2]
        )
        df = df.reset_index().set_index(['sid', 'type'])
        df = df.sort_index().unstack('type')
        del df['index']
        assert isinstance(df, pd.DataFrame)
        return df
