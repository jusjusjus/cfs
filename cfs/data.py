
from os.path import join, exists, dirname, splitext
from functools import cached_property
import xml.etree.ElementTree as ET

import pandas as pd

from .resources import root_dir, metafile
from edfpy import EDF


# The dict translates the Profusion AASM sleep-staging codes into the stage
# names.

sleep_stage_map = {
    0: 'Wake',
    1: 'N1',
    2: 'N2',
    3: 'N3',
    5: 'R'
}


class Dataset:

    def __getitem__(self, subject_id):
        if isinstance(subject_id, int):
            subject_id = self.subject_ids[subject_id]

        entry = {
            'edf': self.edf(subject_id),
            'xml': self.xml(subject_id),
            'sid': subject_id
        }
        info = self.subject_info(subject_id, as_dict=True)
        if info:
            entry.update(**info)

        return entry

    def __len__(self):
        return len(self.subject_ids)

    def edf(self, subject_id):
        filename = join(root_dir, self.files.loc[subject_id].filenames.edf)
        return EDF.read_file(filename)

    def xml(self, subject_id):
        filename = join(root_dir, self.files.loc[subject_id].filenames.xml)
        root = ET.parse(filename).getroot()

        def find(tag):
            element = root.find(tag)
            assert element is not None, f"Missing tag '{tag}'"
            return element

        try:
            element = find('EpochLength')
            text = element.text
            assert isinstance(text, str), f"Error in 'EpochLength' {text}"
            duration = float(text)
            el = find('SleepStages')
            xml_stages = el.getchildren()
        except AttributeError as err:
            raise ValueError(f"Broken xml file: {str(err)}")

        int_stages = map(int, (x.text for x in xml_stages))  # type: ignore
        stage_labels = list(map(sleep_stage_map.get, int_stages))
        df = pd.DataFrame(data={
            't0': [s * duration for s in range(len(stage_labels))],
            'dt': duration,
            'stage': stage_labels
        })
        df = df[df.stage.apply(lambda x: x is not None)]
        df = df[['t0', 'dt', 'stage']]
        return df

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
