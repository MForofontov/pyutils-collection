"""Known-answer cases for small and unevenly spaced derivative inputs."""

import numpy as np

import pytest
from pyutils_collection.scientific_computing_functions.numerical_methods.numerical_derivative import (
    numerical_derivative,
)

pytestmark = [pytest.mark.unit, pytest.mark.scientific_computing]


def test_gradient_accepts_two_points():
    result = numerical_derivative([1.0, 3.0], [4.0, 10.0], method="gradient")
    np.testing.assert_allclose(result["derivative"], [3.0, 3.0])


@pytest.mark.parametrize("x", [[0.0, 1.0, 3.0, 6.0], [6.0, 3.0, 1.0, 0.0]])
def test_central_quadratic_on_nonuniform_grid(x):
    values = np.array(x)
    result = numerical_derivative(x, (values**2).tolist())
    np.testing.assert_allclose(result["derivative"][1:-1], 2 * values[1:-1])
