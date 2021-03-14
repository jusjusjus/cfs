from os.path import dirname, join
import pytest
from cfs.profusion import Profusion


@pytest.fixture
def profusion():
    filepath = join(dirname(__file__), '..', 'examples', 'profusion.xml')
    return Profusion.read(filepath)


def test_epoch_length(profusion):
    assert profusion.epoch_length == 30.0


def test_sleep_stages(profusion):
    expected = 'Wake N1 N2 N3 S4 R'.split()
    assert profusion.sleep_stages == expected
