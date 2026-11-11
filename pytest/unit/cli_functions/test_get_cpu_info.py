import pytest

try:
    import psutil
    from pyutils_collection.cli_functions.get_cpu_info import get_cpu_info
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    get_cpu_info = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.cli_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_get_cpu_info_returns_valid_dict() -> None:
    """
    Test case 1: The get_cpu_info function returns a valid dictionary with CPU information.
    """
    cpu_info = get_cpu_info()

    # Check return type
    assert isinstance(cpu_info, dict)

    # Check required keys
    required_keys = ["cpu_count", "cpu_percent", "cpu_percent_per_core"]
    for key in required_keys:
        assert key in cpu_info

    # Check cpu_count
    assert isinstance(cpu_info["cpu_count"], int)
    assert cpu_info["cpu_count"] > 0

    # Check cpu_percent
    assert isinstance(cpu_info["cpu_percent"], (int, float))
    assert 0 <= cpu_info["cpu_percent"] <= 100

    # Check cpu_percent_per_core
    assert isinstance(cpu_info["cpu_percent_per_core"], list)
    assert len(cpu_info["cpu_percent_per_core"]) == cpu_info["cpu_count"]


def test_get_cpu_info_custom_interval() -> None:
    """
    Test case 2: Test get_cpu_info with custom interval parameter.
    """
    cpu_info = get_cpu_info(interval=0.05)

    assert isinstance(cpu_info, dict)
    assert "cpu_percent" in cpu_info
    assert isinstance(cpu_info["cpu_percent"], (int, float))


def test_get_cpu_info_per_core_percents_valid() -> None:
    """
    Test case 3: Verify per-core CPU percentages are valid.
    """
    cpu_info = get_cpu_info()
    per_core_percents = cpu_info["cpu_percent_per_core"]

    for core_percent in per_core_percents:
        assert isinstance(core_percent, (int, float))
        assert 0 <= core_percent <= 100


def test_get_cpu_info_frequency_info() -> None:
    """
    Test case 4: Verify CPU frequency information is present and valid.
    """
    cpu_info = get_cpu_info()

    # Frequency keys should exist
    assert "cpu_freq_current" in cpu_info
    assert "cpu_freq_min" in cpu_info
    assert "cpu_freq_max" in cpu_info

    # If frequency is available, validate values
    if cpu_info["cpu_freq_current"] is not None:
        assert cpu_info["cpu_freq_current"] > 0


def test_get_cpu_info_load_average() -> None:
    """
    Test case 5: Verify load average information is present.
    """
    cpu_info = get_cpu_info()

    assert "load_average" in cpu_info
    # Load average may be None on Windows
    if cpu_info["load_average"] is not None:
        assert isinstance(cpu_info["load_average"], tuple)
        assert len(cpu_info["load_average"]) == 3


def test_get_cpu_info_consistency() -> None:
    """
    Test case 6: Verify consistency between multiple calls.
    """
    cpu_info1 = get_cpu_info(interval=0.01)
    cpu_info2 = get_cpu_info(interval=0.01)

    # CPU count should be consistent
    assert cpu_info1["cpu_count"] == cpu_info2["cpu_count"]
    # Per-core list length should be consistent
    assert len(cpu_info1["cpu_percent_per_core"]) == len(
        cpu_info2["cpu_percent_per_core"]
    )


@pytest.mark.parametrize("availability", ["missing", "not_implemented"])
def test_get_cpu_info_when_frequency_is_unavailable(monkeypatch, availability):
    if availability == "missing":
        monkeypatch.delattr(psutil, "cpu_freq", raising=False)
    else:
        def unavailable():
            raise NotImplementedError("frequency is unavailable on this platform")

        monkeypatch.setattr(psutil, "cpu_freq", unavailable, raising=False)
    info = get_cpu_info(interval=0)
    assert info["cpu_count"] > 0
    assert info["cpu_freq_current"] is None
    assert info["cpu_freq_min"] is None
    assert info["cpu_freq_max"] is None
