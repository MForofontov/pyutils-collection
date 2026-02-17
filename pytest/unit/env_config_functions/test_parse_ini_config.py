import configparser

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.env_config]
from pyutils_collection.env_config_functions.parse_ini_config import parse_ini_config


def write_ini_file(data, path):
    parser = configparser.ConfigParser()
    for section, values in data.items():
        parser[section] = values
    with open(path, "w") as f:
        parser.write(f)


def test_parse_ini_config_basic(tmp_path) -> None:

    """
    Test case 1: Basic INI config loads as dict.
    """
    data = {"section1": {"a": "1"}, "section2": {"b": "2"}}
    config_file = tmp_path / "config.ini"
    write_ini_file(data, config_file)
    config = parse_ini_config(str(config_file))
    assert config == data


def test_parse_ini_config_required_sections(tmp_path) -> None:

    """
    Test case 2: Missing required sections raises ValueError.
    """
    data = {"section1": {"a": "1"}}
    config_file = tmp_path / "config.ini"
    write_ini_file(data, config_file)
    with pytest.raises(ValueError, match="Missing required config sections"):
        parse_ini_config(str(config_file), required_sections=["section1", "section2"])


def test_parse_ini_config_schema_validator(tmp_path) -> None:

    """
    Test case 3: Custom schema validator raises ValueError.
    """
    data = {"section1": {"a": "1"}}

    def schema(cfg):
        if "section2" not in cfg:
            raise ValueError("section2 required")

    config_file = tmp_path / "config.ini"
    write_ini_file(data, config_file)
    with pytest.raises(ValueError, match="section2 required"):
        parse_ini_config(str(config_file), schema_validator=schema)


def test_parse_ini_config_file_not_found(tmp_path) -> None:

    """
    Test case 4: Missing INI files raise FileNotFoundError.
    """

    missing_file = tmp_path / "missing.ini"

    with pytest.raises(FileNotFoundError):
        parse_ini_config(str(missing_file))


def test_parse_ini_config_invalid_format(tmp_path) -> None:

    """
    Test case 5: Invalid INI content raises configparser.Error.
    """

    config_file = tmp_path / "config.ini"
    config_file.write_text("key=value\n")

    with pytest.raises(configparser.Error):
        parse_ini_config(str(config_file))
