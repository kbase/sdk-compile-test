import datetime
from pytest import raises
from core.test_utils import assert_exception_correct
from SampleService.core.arg_checkers import check_string, not_falsy, not_falsy_in_iterable
from SampleService.core.arg_checkers import check_timestamp
from SampleService.core.errors import MissingParameterError, IllegalParameterError

LONG_STRING = 'a' * 100


def test_falsy_true():
    for t in ['a', 1, True, [1], {'a': 1}, {1}]:
        assert not_falsy(t, 'foo') is t


def test_falsy_fail():
    for f in ['', 0, False, [], dict(), {}]:
        with raises(Exception) as got:
            not_falsy(f, 'my name')
        assert_exception_correct(
            got.value, ValueError('my name cannot be a value that evaluates to false'))


def test_falsy_in_iterable_true():
    for t in [[], [1, 'a'], [True], [{'foo'}]]:
        assert not_falsy_in_iterable(t, 'foo') is t


def test_falsy_in_iterable_allow_none():
    assert not_falsy_in_iterable(None, 'yay', allow_none=True) is None


def test_falsy_in_iterable_no_iterable():
    with raises(Exception) as got:
        not_falsy_in_iterable(None, 'whee')
    assert_exception_correct(got.value, ValueError('whee cannot be None'))


def test_falsy_in_iterable_false_insides():
    for item, pos in [[['', 'bar'], 0],
                      [['foo', 0], 1],
                      [[True, True, False, True], 2],
                      [[[]], 0],
                      [[dict()], 0],
                      [[{}], 0]
                      ]:
        with raises(Exception) as got:
            not_falsy_in_iterable(item, 'my name')
        assert_exception_correct(got.value, ValueError(
            f'Index {pos} of iterable my name cannot be a value that evaluates to false'))


def test_check_string():
    for string, expected in {'    foo': 'foo',
                             '  \t   baɷr     ': 'baɷr',
                             'baᚠz  \t  ': 'baᚠz',
                             'bat': 'bat',
                             'a' * 1000: 'a' * 1000}.items():
        assert check_string(string, 'name') == expected


def test_check_string_bad_max_len():
    for max_len in [0, -1, -100]:
        with raises(Exception) as got:
            check_string('str', 'var name', max_len=max_len)
        assert_exception_correct(got.value, ValueError('max_len must be > 0 if provided'))


def test_check_string_optional_true():
    for string in [None, '   \t   ']:
        assert check_string(string, 'name', optional=True) is None


def test_check_string_optional_false():
    for string in [None, '   \t   ']:
        with raises(Exception) as got:
            check_string(string, 'var name')
        assert_exception_correct(got.value, MissingParameterError('var name'))


def test_check_string_control_characters():
    for string in ['foo \b  bar', 'foo\u200bbar', 'foo\0bar', 'foo\bbar']:
        with raises(Exception) as got:
            check_string(string, 'var name')
        assert_exception_correct(
            got.value, IllegalParameterError('var name contains control characters'))


def test_check_string_max_len():
    for string, length in {'123456789': 9,
                           'a': 1,
                           'a' * 100: 100,
                           'a' * 10000: 10000,
                           'a' * 10000: 1000000}.items():
        assert check_string(string, 'name', max_len=length) == string


def test_check_string_long_fail():
    for string, length in {'123456789': 8,
                           'ab': 1,
                           'a' * 100: 99}.items():
        with raises(Exception) as got:
            check_string(string, 'var name', max_len=length)
        assert_exception_correct(
            got.value, IllegalParameterError(f'var name exceeds maximum length of {length}'))


def _dt(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)


def test_check_timestamp():
    for t in [-1000000, -256, -1, 0, 1, 6, 100, 100000000000]:
        assert check_timestamp(_dt(t), 'name') == _dt(t)


def test_check_timestamp_fail_bad_args():
    _check_timestamp_fail(None, 'ts', ValueError('ts cannot be a value that evaluates to false'))
    _check_timestamp_fail(datetime.datetime.now(), 'tymestampz', ValueError(
        'tymestampz cannot be a naive datetime'))


def _check_timestamp_fail(ts, name, expected):
    with raises(Exception) as got:
        check_timestamp(ts, name)
    assert_exception_correct(got.value, expected)
