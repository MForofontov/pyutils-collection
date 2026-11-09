"""
Streaming aggregator for on-the-fly data aggregation with running statistics.
"""

from typing import Any


class StreamingAggregator:
    """
    On-the-fly data aggregation with running statistics.

    Computes statistics incrementally without storing all values in memory.
    Useful for processing infinite streams or very large datasets where
    storing all values is impractical.

    Attributes
    ----------
    count : int
        Number of values processed.
    sum : float
        Running sum of values.
    min_value : float | None
        Minimum value seen.
    max_value : float | None
        Maximum value seen.

    Examples
    --------
    >>> agg = StreamingAggregator()
    >>> for value in [1, 2, 3, 4, 5]:
    ...     agg.add(value)
    >>> agg.mean
    3.0
    >>> agg.count
    5

    >>> # Reset and reuse
    >>> agg.reset()
    >>> agg.count
    0

    Notes
    -----
    The streaming aggregator uses Welford's online algorithm for variance
    calculation, which is numerically stable and requires only O(1) space.

    This is essential for:
    - Processing infinite data streams
    - Computing stats on datasets too large for memory
    - Real-time monitoring and dashboards

    Complexity
    ----------
    Time: O(1) per value added, Space: O(1)
    """

    def __init__(self) -> None:
        """Initialize streaming aggregator with zero state."""
        self.count = 0
        self.sum = 0.0
        self.min_value: float | None = None
        self.max_value: float | None = None
        self._mean = 0.0
        self._m2 = 0.0  # For variance calculation (Welford's algorithm)

    def add(self, value: float) -> None:
        """
        Add a value to the aggregator.

        Parameters
        ----------
        value : float
            Value to add to the aggregation.

        Raises
        ------
        TypeError
            If value is not a number.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add(10.5)
        >>> agg.count
        1
        >>> agg.sum
        10.5
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"value must be a number, got {type(value).__name__}")

        self.count += 1
        self.sum += value

        # Update min/max
        if self.min_value is None or value < self.min_value:
            self.min_value = value
        if self.max_value is None or value > self.max_value:
            self.max_value = value

        # Welford's online algorithm for mean and variance
        delta = value - self._mean
        self._mean += delta / self.count
        delta2 = value - self._mean
        self._m2 += delta * delta2

    def add_batch(self, values: list[float]) -> None:
        """
        Add multiple values at once.

        Parameters
        ----------
        values : list[float]
            List of values to add.

        Raises
        ------
        TypeError
            If values is not a list or contains non-numeric values.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add_batch([1, 2, 3, 4, 5])
        >>> agg.count
        5
        """
        if not isinstance(values, list):
            raise TypeError(f"values must be a list, got {type(values).__name__}")

        for value in values:
            self.add(value)

    @property
    def mean(self) -> float:
        """
        Get the mean of all values added.

        Returns
        -------
        float
            Mean value, or 0.0 if no values added.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add_batch([2, 4, 6])
        >>> agg.mean
        4.0
        """
        return self._mean if self.count > 0 else 0.0

    @property
    def variance(self) -> float:
        """
        Get the variance of all values added.

        Returns
        -------
        float
            Sample variance, or 0.0 if fewer than 2 values.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add_batch([2, 4, 6, 8])
        >>> round(agg.variance, 2)
        6.67
        """
        if self.count < 2:
            return 0.0
        return self._m2 / (self.count - 1)

    @property
    def std_dev(self) -> float:
        """
        Get the standard deviation of all values added.

        Returns
        -------
        float
            Sample standard deviation, or 0.0 if fewer than 2 values.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add_batch([2, 4, 6, 8])
        >>> round(agg.std_dev, 2)
        2.58
        """
        return self.variance**0.5  # type: ignore[no-any-return]

    def get_stats(self) -> dict[str, Any]:
        """
        Get all statistics as a dictionary.

        Returns
        -------
        dict[str, Any]
            Dictionary containing all computed statistics.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add_batch([1, 2, 3])
        >>> stats = agg.get_stats()
        >>> stats['count']
        3
        >>> stats['mean']
        2.0
        """
        return {
            "count": self.count,
            "sum": self.sum,
            "mean": self.mean,
            "min": self.min_value,
            "max": self.max_value,
            "variance": self.variance,
            "std_dev": self.std_dev,
        }

    def reset(self) -> None:
        """
        Reset the aggregator to initial state.

        Examples
        --------
        >>> agg = StreamingAggregator()
        >>> agg.add_batch([1, 2, 3])
        >>> agg.reset()
        >>> agg.count
        0
        """
        self.count = 0
        self.sum = 0.0
        self.min_value = None
        self.max_value = None
        self._mean = 0.0
        self._m2 = 0.0

    def merge(self, other: StreamingAggregator) -> None:
        """
        Merge statistics from another aggregator.

        Parameters
        ----------
        other : StreamingAggregator
            Another aggregator to merge with this one.

        Raises
        ------
        TypeError
            If other is not a StreamingAggregator instance.

        Examples
        --------
        >>> agg1 = StreamingAggregator()
        >>> agg1.add_batch([1, 2, 3])
        >>> agg2 = StreamingAggregator()
        >>> agg2.add_batch([4, 5, 6])
        >>> agg1.merge(agg2)
        >>> agg1.count
        6
        >>> agg1.mean
        3.5

        Notes
        -----
        This uses Chan's parallel variance algorithm for combining
        statistics from independent streams.
        """
        if not isinstance(other, StreamingAggregator):
            raise TypeError(
                f"other must be a StreamingAggregator, got {type(other).__name__}"
            )

        if other.count == 0:
            return

        if self.count == 0:
            self.count = other.count
            self.sum = other.sum
            self.min_value = other.min_value
            self.max_value = other.max_value
            self._mean = other._mean
            self._m2 = other._m2
            return

        # Merge min/max
        if other.min_value is not None:
            if self.min_value is None or other.min_value < self.min_value:
                self.min_value = other.min_value
        if other.max_value is not None:
            if self.max_value is None or other.max_value > self.max_value:
                self.max_value = other.max_value

        # Chan's parallel variance algorithm
        total_count = self.count + other.count
        delta = other._mean - self._mean
        self._m2 = (
            self._m2
            + other._m2
            + (delta * delta * self.count * other.count / total_count)
        )
        self._mean = (self.count * self._mean + other.count * other._mean) / total_count
        self.count = total_count
        self.sum += other.sum


__all__ = ["StreamingAggregator"]
