#!/usr/bin/env python3
"""An exact local counterexample to the sample-count assertion in AFML 16.3.

This is an independent test oracle, not a port of HRP and not a performance kernel.
The book's original text remains untouched. See ERR-0001 for scope and limitations.
"""
from __future__ import annotations

import json
from fractions import Fraction
from typing import Sequence

Rational = int | Fraction
Matrix = list[list[Fraction]]


def sample_covariance(observations: Sequence[Sequence[Rational]]) -> Matrix:
    """Return centered unbiased covariance using exact rational arithmetic.

    Requires at least two observations of the same nonzero dimension. Only exact
    integers/Fractions are accepted: silently converting binary floats would defeat
    this oracle's explicit exact-input contract.
    """
    count = len(observations)
    if count < 2:
        raise ValueError('At least two observations are required.')
    dimension = len(observations[0])
    if dimension == 0 or any(len(row) != dimension for row in observations):
        raise ValueError('Observations must have the same nonzero dimension.')
    if any(type(value) not in (int, Fraction) for row in observations for value in row):
        raise TypeError('The exact oracle accepts only integers and Fractions.')
    means = [sum((Fraction(row[column]) for row in observations), Fraction(0)) / count for column in range(dimension)]
    covariance = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for left in range(dimension):
        for right in range(dimension):
            covariance[left][right] = sum(
                ((row[left] - means[left]) * (row[right] - means[right]) for row in observations),
                Fraction(0),
            ) / (count - 1)
    return covariance


def determinant(matrix: Sequence[Sequence[Rational]]) -> Fraction:
    """Exact determinant by Gaussian elimination with row swaps.

    The determinant of the empty 0-by-0 matrix is one. A non-square matrix or a
    floating-point entry is rejected. The input is not mutated.
    """
    dimension = len(matrix)
    if any(len(row) != dimension for row in matrix):
        raise ValueError('A determinant requires a square matrix.')
    if any(type(value) not in (int, Fraction) for row in matrix for value in row):
        raise TypeError('The exact oracle accepts only integers and Fractions.')
    work = [[Fraction(value) for value in row] for row in matrix]
    result = Fraction(1)
    for column in range(dimension):
        pivot = next((row for row in range(column, dimension) if work[row][column] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, dimension):
            multiplier = work[row][column] / pivot_value
            for entry in range(column + 1, dimension):
                work[row][entry] -= multiplier * work[column][entry]
            work[row][column] = Fraction(0)
    return result


def counterexample() -> dict[str, object]:
    observations = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
    covariance = sample_covariance(observations)
    value = determinant(covariance)
    return {
        'source_issue': 'ERR-0001',
        'observations': observations,
        'dimension': 3,
        'sample_count': 4,
        'book_asserted_minimum': 6,
        'covariance': [[str(entry) for entry in row] for row in covariance],
        'determinant': str(value),
        'nonsingular_with_fewer_than_asserted_minimum': value != 0 and 4 < 6,
        'statistical_estimation_adequacy_claimed': False,
        'publisher_confirmation': False,
    }


if __name__ == '__main__':
    print(json.dumps(counterexample(), indent=2))
