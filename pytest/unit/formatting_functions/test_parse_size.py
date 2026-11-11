"""Unit tests for parse_size function."""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.formatting]
from pyutils_collection.formatting_functions.parse_size import parse_size


def test_parse_size_kilobytes_binary() -> None:
    """
    Test case 1: Parse kilobytes with binary units.
    """
    # Arrange & Act & Assert
    assert parse_size("1 KiB") == 1024
    assert parse_size("1.5 KiB") == 1536
    assert parse_size("2 KB") == 2048  # KB treated as binary by default
    assert parse_size("1 K") == 1024


def test_parse_size_kilobytes_decimal() -> None:
    """
    Test case 2: Parse kilobytes with decimal units.
    """
    # Arrange & Act & Assert
    assert parse_size("1 KB", binary=False) == 1000
    assert parse_size("1.5 KB", binary=False) == 1500
    assert parse_size("2 K", binary=False) == 2000


def test_parse_size_megabytes() -> None:
    """
    Test case 3: Parse megabytes.
    """
    # Arrange & Act & Assert
    assert parse_size("1 MiB") == 1048576
    assert parse_size("1.5 MB") == 1572864  # binary
    assert parse_size("1.5 MB", binary=False) == 1500000


def test_parse_size_gigabytes() -> None:
    """
    Test case 4: Parse gigabytes.
    """
    # Arrange & Act & Assert
    assert parse_size("1 GiB") == 1073741824
    assert parse_size("1.5 GB") == 1610612736  # binary
    assert parse_size("1.5 GB", binary=False) == 1500000000


def test_parse_size_terabytes() -> None:
    """
    Test case 5: Parse terabytes.
    """
    # Arrange & Act & Assert
    assert parse_size("1 TiB") == 1099511627776
    assert parse_size("2 TB", binary=False) == 2000000000000


def test_parse_size_bytes_only() -> None:
    """
    Test case 6: Parse size with bytes only.
    """
    # Arrange & Act & Assert
    assert parse_size("0") == 0
    assert parse_size("512") == 512
    assert parse_size("1024") == 1024
    assert parse_size("0 B") == 0
    assert parse_size("512 B") == 512


def test_parse_size_case_insensitive() -> None:
    """
    Test case 7: Parse is case-insensitive.
    """
    # Arrange & Act & Assert
    assert parse_size("1 mb") == 1048576
    assert parse_size("1 MB") == 1048576
    assert parse_size("1 Mb") == 1048576
    assert parse_size("1 mib") == 1048576


def test_parse_size_whitespace_handling() -> None:
    """
    Test case 8: Handle various whitespace formats.
    """
    # Arrange & Act & Assert
    assert parse_size("1MB") == 1048576
    assert parse_size("1 MB") == 1048576
    assert parse_size(" 1 MB ") == 1048576
    assert parse_size("1  MB") == 1048576


def test_parse_size_decimal_numbers() -> None:
    """
    Test case 9: Parse decimal number values.
    """
    # Arrange & Act & Assert
    assert parse_size("0.5 MB") == 524288
    assert parse_size("1.25 GB") == 1342177280
    assert parse_size("2.5 KB") == 2560


def test_parse_size_large_units() -> None:
    """
    Test case 10: Parse large units (PB, EB, etc.).
    """
    # Arrange & Act & Assert
    assert parse_size("1 PB", binary=False) == 1000000000000000
    assert parse_size("1 EB", binary=False) == 1000000000000000000


def test_parse_size_round_trip_consistency() -> None:
    """
    Test case 11: Verify round-trip consistency with format_file_size.
    """
    # This test verifies that parsing formatted sizes returns close to original
    from pyutils_collection.formatting_functions.format_file_size import format_file_size

    # Arrange
    original_sizes = [1024, 1048576, 1073741824]

    # Act & Assert
    for size in original_sizes:
        formatted = format_file_size(size, precision=0)
        parsed = parse_size(formatted)
        # Should be equal or very close (within rounding)
        assert abs(parsed - size) <= size * 0.01  # Within 1%


def test_parse_size_invalid_type_size_str() -> None:
    """
    Test case 12: TypeError for non-string input.
    """
    # Arrange
    expected_message = "size_str must be a string, got int"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        parse_size(1024)


def test_parse_size_invalid_type_binary() -> None:
    """
    Test case 13: TypeError for invalid binary type.
    """
    # Arrange
    expected_message = "binary must be a boolean, got str"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        parse_size("1 MB", binary="true")


def test_parse_size_empty_string() -> None:
    """
    Test case 14: ValueError for empty string.
    """
    # Arrange
    expected_message = "size_str cannot be empty"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        parse_size("")

    with pytest.raises(ValueError, match=expected_message):
        parse_size("   ")


def test_parse_size_invalid_format() -> None:
    """
    Test case 15: ValueError for invalid format.
    """
    # Arrange
    expected_message = "Invalid size format|Invalid number in size string"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        parse_size("abc")

    with pytest.raises(ValueError, match=expected_message):
        parse_size("1.2.3 MB")


def test_parse_size_invalid_number() -> None:
    """
    Test case 16: ValueError for invalid number.
    """
    # Arrange
    expected_message = "Invalid number in size string"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        parse_size("..5 MB")


def test_parse_size_negative_value() -> None:
    """
    Test case 17: ValueError for negative size.
    """
    # Arrange
    expected_message = "Invalid size format"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        parse_size("-1 MB")


def test_parse_size_unknown_unit() -> None:
    """
    Test case 18: ValueError for unknown unit.
    """
    # Arrange
    expected_message = "Unknown unit"

    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        parse_size("1 XB")

    with pytest.raises(ValueError, match=expected_message):
        parse_size("1 INVALID")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("9007199254740993 B", 9007199254740993),
        ("8796093022208.0009765625 KiB", 9007199254740993),
        ("0.99999999999999999999 B", 0),
    ],
)
def test_parse_size_preserves_exact_decimal_bytes(value, expected):
    assert parse_size(value) == expected
