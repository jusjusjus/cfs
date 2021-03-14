from os.path import join, exists, dirname, splitext
from functools import cached_property, lru_cache

import pandas as pd
from edfpy import EDF

from .resources import root_dir, metafile
from .profusion import Profusion

cache = lru_cache


class Dataset:

    def __getitem__(self, subject_id):
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

    def __len__(self):
        return len(self.subject_ids)

    @cache
    def edf(self, subject_id):
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        filename = join(root_dir, self.files.loc[subject_id].filenames.edf)
        return EDF.read_file(filename)

    @cache
    def xml(self, subject_id):
        filepath = join(root_dir, self.files.loc[subject_id].filenames.xml)
        profusion = Profusion.read(filepath)
        dt = profusion.epoch_length
        labels = profusion.sleep_stages
        t0 = [s * dt for s in range(len(labels))]
        df = pd.DataFrame(data={
            't0': t0, 'dt': dt, 'stage': labels
        })
        df = df[df.stage.apply(lambda x: x is not None)]
        return df[['t0', 'dt', 'stage']]

    @cached_property
    def subject_ids(self):
        return list(self.files.index)

    def subject_info(self, subject_id, as_dict=False):
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        info = self._subject_info.loc[subject_id].dropna()
        return info.to_dict() if as_dict else info

    @cached_property
    def _subject_info(self):
        df = pd.read_csv(metafile)
        df['nsrrid'] = df.nsrrid.apply(str)
        df.set_index('nsrrid', inplace=True)
        return df

    @cached_property
    def files(self):
        filename = join(dirname(__file__), "md5sums.txt")
        assert exists(filename), f"md5sums not found ({filename})"
        df = pd.read_csv(filename, sep='  ', header=None, engine='python')
        df.columns = ['md5sum', 'filenames']
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
        return df
