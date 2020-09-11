import pytest
import numpy as np
import mymath.bindings


def test_dot():

    v1 = [1., 2, 3, -5.5, 42]
    v2 = [-3.2, 0, 13, 6, -3.14]

    result = mymath.bindings.dot(vector1=v1, vector2=v2)
    assert pytest.approx(result) == np.dot(v1, v2)


def test_normalize():

    v = [1., 2, 3, -5.5, 42]

    result = mymath.bindings.normalize(input=v)
    assert pytest.approx(result) == np.array(v) / np.linalg.norm(v)


def test_dot_numpy():

    v1 = np.array([1., 2, 3, -5.5, 42])
    v2 = np.array([-3.2, 0, 13, 6, -3.14])

    result = mymath.bindings.dot_numpy(in_1=v1, in_2=v2)
    assert pytest.approx(result) == np.dot(v1, v2)


def test_normalize_numpy():

    v = np.array([1., 2, 3, -5.5, 42])

    result = mymath.bindings.normalize_numpy(in_1=v)

    assert isinstance(result, np.ndarray)
    assert pytest.approx(result) == np.array(v) / np.linalg.norm(v)


def test_assertion():

    v1 = np.array([1., 2, 3, -5.5])
    v2 = np.array([42.])

    with pytest.raises(RuntimeError):
        _ = mymath.bindings.dot_numpy(in_1=v1, in_2=v2)
