from typing import List, Dict, Optional
from functools import cached_property
import xml.etree.ElementTree as ET


sleep_stage_map: Dict[int, Optional[str]] = {
    0: 'Wake',
    1: 'N1',
    2: 'N2',
    3: 'N3',
    4: None,
    5: 'R'
}


class Profusion:

    def __init__(self, root):
        self.root = root

    @classmethod
    def read(cls, filepath: str):
        root = ET.parse(filepath).getroot()
        return cls(root)

    @cached_property
    def epoch_length(self) -> float:
        element = self.find('EpochLength')
        return float(element.text)

    @cached_property
    def sleep_stages(self) -> List[Optional[str]]:
        element = self.find('SleepStages')
        stages_txt = map(lambda el: el.text, list(element))
        stages_int = map(int, stages_txt)
        stages = map(sleep_stage_map.get, stages_int)
        return list(stages)

    def find(self, tag: str, root=None):
        root = root or self.root
        element = root.find(tag)
        assert element is not None, f"Missing tag '{tag}'"
        return element
