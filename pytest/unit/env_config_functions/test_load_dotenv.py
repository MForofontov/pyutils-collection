import pytest

try:
    import os
    from pyutils_collection.env_config_functions.load_dotenv import load_dotenv
    PYYAML_AVAILABLE = True
except ImportError:
    PYYAML_AVAILABLE = False
    os = None  # type: ignore
    load_dotenv = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.env_config,
    pytest.mark.skipif(not PYYAML_AVAILABLE, reason="pyyaml not installed"),
]


def test_load_dotenv_basic(tmp_path) -> None:

    """
    Test case 1: Basic .env file loading.
    """
    config_file = tmp_path / "config.env"
    config_file.write_text("FOO=bar\nBAZ=qux\n")
    # Clear env vars first
    os.environ.pop("FOO", None)
    os.environ.pop("BAZ", None)
    load_dotenv(str(config_file))
    assert os.environ["FOO"] == "bar"
    assert os.environ["BAZ"] == "qux"


def test_load_dotenv_override(tmp_path) -> None:

    """
    Test case 2: Override existing environment variables.
    """
    os.environ["EXISTING"] = "old"
    config_file = tmp_path / "config.env"
    config_file.write_text("EXISTING=new\n")
    load_dotenv(str(config_file), override=True)
    assert os.environ["EXISTING"] == "new"


def test_load_dotenv_no_override(tmp_path) -> None:

    """
    Test case 3: Don't override existing environment variables.
    """
    os.environ["EXISTING"] = "old"
    config_file = tmp_path / "config.env"
    config_file.write_text("EXISTING=new\n")
    load_dotenv(str(config_file), override=False)
    assert os.environ["EXISTING"] == "old"


def test_load_dotenv_comments(tmp_path) -> None:

    """
    Test case 4: Skip comments and empty lines.
    """
    config_file = tmp_path / "config.env"
    config_file.write_text(
        "# This is a comment\nVAR1=value1\n\n# Another comment\nVAR2=value2\n"
    )
    os.environ.pop("VAR1", None)
    os.environ.pop("VAR2", None)
    load_dotenv(str(config_file))
    assert os.environ["VAR1"] == "value1"
    assert os.environ["VAR2"] == "value2"


def test_load_dotenv_nonexistent_file() -> None:

    """
    Test case 5: Nonexistent file returns None and leaves environment untouched.
    """
    load_dotenv("nonexistent.env")  # Should not raise


def test_load_dotenv_empty_file(tmp_path) -> None:

    """
    Test case 6: Empty .env file.
    """
    config_file = tmp_path / "empty.env"
    config_file.write_text("")
    load_dotenv(str(config_file))  # Should not raise


def test_load_dotenv_malformed_lines(tmp_path) -> None:

    """
    Test case 7: File with malformed lines (no equals sign).
    """
    config_file = tmp_path / "malformed.env"
    config_file.write_text("VAR1=value1\nMALFORMED_LINE\nVAR2=value2\n")
    os.environ.pop("VAR1", None)
    os.environ.pop("VAR2", None)
    load_dotenv(str(config_file))
    assert os.environ["VAR1"] == "value1"
    assert os.environ["VAR2"] == "value2"


def test_load_dotenv_quoted_values(tmp_path) -> None:

    """
    Test case 8: Values with quotes.
    """
    config_file = tmp_path / "quoted.env"
    config_file.write_text("VAR1=\"quoted value\"\nVAR2='single quoted'\n")
    os.environ.pop("VAR1", None)
    os.environ.pop("VAR2", None)
    load_dotenv(str(config_file))
    assert os.environ["VAR1"] == "quoted value"
    assert os.environ["VAR2"] == "single quoted"


def test_load_dotenv_invalid_dotenv_path_type() -> None:

    """
    Test case 9: Test load_dotenv with invalid dotenv_path type.
    """
    with pytest.raises(TypeError):
        load_dotenv(123)


def test_load_dotenv_invalid_override_type() -> None:

    """
    Test case 10: Test load_dotenv with invalid override type.
    """
    with pytest.raises(TypeError):
        load_dotenv(".env", override="invalid")
