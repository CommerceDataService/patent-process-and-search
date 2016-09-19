import pytest
from partitioner import Partitioner


def test_throws_exception_when_worker_id_exceeds_num_workers():
    with pytest.raises(RuntimeError) as excinfo:
        p = Partitioner(range(1, 10), 9, 2)

    assert 'Worker id cannot exceed number of workers' == str(excinfo.value)


def test_throws_exceptions_for_worker_0():
    with pytest.raises(RuntimeError) as excinfo:
        p = Partitioner(range(1, 10), 0, 2)

    assert 'Worker id cannot be 0' == str(excinfo.value)


def test_when_only_one_worker_each_obj_is_mine():
    p = Partitioner(range(1, 10), 1, 1)

    assert p.is_mine(0) == True
    assert p.is_mine(1) == True
    assert p.is_mine(2) == True
    assert p.is_mine(3) == True
    assert p.is_mine(933) == True


def test_with_two_workload_is_spread_by_half():
    p = Partitioner(range(1, 10), 1, 2)

    assert p.is_mine(0) == True
    assert p.is_mine(1) == False
    assert p.is_mine(2) == True
    assert p.is_mine(3) == False
    assert p.is_mine(933) == False
    assert p.is_mine(934) == True

    p = Partitioner(range(1, 10), 2, 2)

    assert p.is_mine(0) == False
    assert p.is_mine(1) == True
    assert p.is_mine(2) == False
    assert p.is_mine(3) == True
    assert p.is_mine(933) == True
    assert p.is_mine(934) == False


def test_can_handle_7_workers():
    p = Partitioner(range(1, 10), 1, 7)

    assert p.is_mine(0) == True
    assert p.is_mine(7) == True
    assert p.is_mine(1) == False
    assert p.is_mine(8) == False

    p = Partitioner(range(1, 10), 2, 7)

    assert p.is_mine(1) == True
    assert p.is_mine(22) == True
    assert p.is_mine(0) == False
    assert p.is_mine(7) == False

    p = Partitioner(range(1, 10), 3, 7)

    assert p.is_mine(2) == True
    assert p.is_mine(23) == True
    assert p.is_mine(21) == False
    assert p.is_mine(22) == False
    assert p.is_mine(0) == False
    assert p.is_mine(1) == False


def test_can_get_obj_ids_from_string():
    p = Partitioner(range(1, 10), 3, 7)

    assert p.get_obj_id('Hello') == 139
    assert p.get_obj_id('112') == 127
    assert p.get_obj_id('344') == 179
    assert p.get_obj_id('http://www.google.com') == 237
    assert p.get_obj_id('He' + 'llo') == 139


def test_correctly_partitions_stream():

    def stream():
        return (str(s) for s in range(0,10))

    p = Partitioner(stream(), 1, 3)
    ids = [o for o in p.get_my_stream()]

    assert ids == ['0', '4', '5', '8', '9']
    assert len(ids) == 5

    p = Partitioner(stream(), 2, 3)
    ids = [o for o in p.get_my_stream()]
    assert ids == ['1', '6']
    assert len(ids) == 2

    p = Partitioner(stream(), 3, 3)
    ids = [o for o in p.get_my_stream()]
    assert ids == ['2', '3', '7']
    assert len(ids) == 3


def test_can_initialize_from_go_env_variables():

    import os

    os.environ['GO_JOB_RUN_INDEX'] = '1'
    os.environ['GO_JOB_RUN_COUNT'] = '2'
    p = Partitioner(range(0, 10))

    assert p.is_mine(0) == True
    assert p.is_mine(1) == False
    assert p.is_mine(2) == True
    assert p.is_mine(3) == False
    assert p.is_mine(933) == False
    assert p.is_mine(934) == True


