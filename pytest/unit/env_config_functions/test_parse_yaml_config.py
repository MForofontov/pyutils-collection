try:
    import yaml
    from pyutils_collection.env_config_functions.parse_yaml_config import parse_yaml_config

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None  # type: ignore
    parse_yaml_config = None  # type: ignore

import pytest

pytestmark = pytest.mark.skipif(not YAML_AVAILABLE, reason="pyyaml not installed")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.env_config]


def write_yaml_file(data, path):
    with open(path, "w") as f:
        yaml.safe_dump(data, f)


def test_parse_yaml_config_basic(tmp_path) -> None:

    """
    Test case 1: Basic YAML config loads as dict
    """
    data = {"a": 1, "b": {"c": 2}}
    config_file = tmp_path / "config.yaml"
    write_yaml_file(data, config_file)
    config = parse_yaml_config(str(config_file))
    assert config == data


def test_parse_yaml_config_required_keys(tmp_path) -> None:

    """
    Test case 2: Missing required keys raises ValueError
    """
    data = {"a": 1}
    config_file = tmp_path / "config.yaml"
    write_yaml_file(data, config_file)
    with pytest.raises(ValueError, match="Missing required config keys"):
        parse_yaml_config(str(config_file), required_keys=["a", "b"])


def test_parse_yaml_config_schema_validator(tmp_path) -> None:

    """
    Test case 3: Custom schema validator raises ValueError
    """
    data = {"a": 1}

    def schema(cfg):
        if "b" not in cfg:
            raise ValueError("b required")

    config_file = tmp_path / "config.yaml"
    write_yaml_file(data, config_file)
    with pytest.raises(ValueError, match="b required"):
        parse_yaml_config(str(config_file), schema_validator=schema)


def test_parse_yaml_config_invalid_yaml(tmp_path) -> None:

    """
    Test case 4: Invalid YAML raises yaml.YAMLError
    """
    config_file = tmp_path / "config.yaml"
    config_file.write_text("a: 1\nb: [1, 2\n")  # malformed YAML
    with pytest.raises(yaml.YAMLError):
        parse_yaml_config(str(config_file))


def test_parse_yaml_config_not_dict(tmp_path) -> None:

    """
    Test case 5: YAML that is not a dict raises ValueError
    """
    data = [1, 2, 3]
    config_file = tmp_path / "config.yaml"
    write_yaml_file(data, config_file)
    with pytest.raises(ValueError, match="must be a dictionary"):
        parse_yaml_config(str(config_file))


def test_parse_yaml_config_missing_file(tmp_path) -> None:

    """
    Test case 6: Missing YAML files raise FileNotFoundError
    """

    missing_file = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        parse_yaml_config(str(missing_file))
