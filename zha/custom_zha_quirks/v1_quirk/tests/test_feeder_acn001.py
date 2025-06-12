import pytest
import logging
from zha.custom_zha_quirks.v1_quirk.feeder_acn001 import OppleCluster, DAY_CODES

class DummyLogger:
    def __init__(self):
        self.infos = []
        self.errors = []
    def info(self, *args, **kwargs):
        self.infos.append((args, kwargs))
    def error(self, *args, **kwargs):
        self.errors.append((args, kwargs))

@pytest.fixture
def opple_cluster(monkeypatch):
    # Patch LOGGER in the module to our dummy logger
    dummy_logger = DummyLogger()
    monkeypatch.setattr("zha.custom_zha_quirks.v1_quirk.feeder_acn001.LOGGER", dummy_logger)
    return OppleCluster(), dummy_logger

def test_build_schedule_bytes_single_schedule(opple_cluster):
    cluster, logger = opple_cluster
    # 11=mon, 08=hour, 30=minute, 02=portions
    cluster._build_schedule_bytes("11083002")
    assert logger.infos
    args, kwargs = logger.infos[0]
    assert "Schedule: Day=11" in args[0] or args[0].startswith("Schedule: Day=")
    assert 11 in args
    assert "mon" in args

def test_build_schedule_bytes_multiple_schedules(opple_cluster):
    cluster, logger = opple_cluster
    # Two schedules: mon 08:30 02 portions, tue 09:15 03 portions
    cluster._build_schedule_bytes("1108300212091503")
    assert len(logger.infos) == 2
    # First schedule
    args1, _ = logger.infos[0]
    assert 11 in args1
    assert 8 in args1
    assert 30 in args1
    assert 2 in args1
    # Second schedule
    args2, _ = logger.infos[1]
    assert 12 in args2
    assert 9 in args2
    assert 15 in args2
    assert 3 in args2

def test_build_schedule_bytes_invalid_input(opple_cluster):
    cluster, logger = opple_cluster
    # Not enough digits
    cluster._build_schedule_bytes("1108")
    assert logger.errors
    assert "Schedule parse error" in logger.errors[0][0][0]

def test_build_schedule_bytes_non_digit(opple_cluster):
    cluster, logger = opple_cluster
    # Non-digit input
    cluster._build_schedule_bytes("abcdabcd")
    assert logger.errors
    assert "Schedule parse error" in logger.errors[0][0][0]

def test_build_schedule_bytes_day_code_mapping(opple_cluster):
    cluster, logger = opple_cluster
    # 77 is mapped to 127 (everyday)
    cluster._build_schedule_bytes("77080002")
    assert logger.infos
    args, _ = logger.infos[0]
    assert 77 in args
    assert 8 in args
    assert 0 in args or 8 in args  # hour
    assert 2 in args
    assert "127" in str(args) or "everyday" in str(args)