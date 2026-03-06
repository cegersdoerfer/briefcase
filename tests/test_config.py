import yaml

from briefcase.config import get_default_layout, load_config


def test_load_config_missing_file(tmp_path):
    assert load_config(tmp_path) == {}


def test_load_config_reads_yaml(tmp_path):
    (tmp_path / "config.yaml").write_text(yaml.dump({"default_layout": "minimal"}))
    config = load_config(tmp_path)
    assert config["default_layout"] == "minimal"


def test_load_config_none_home():
    assert load_config(None) == {}


def test_get_default_layout_no_config(tmp_path):
    assert get_default_layout(tmp_path) == "default"


def test_get_default_layout_from_config(tmp_path):
    (tmp_path / "config.yaml").write_text(yaml.dump({"default_layout": "minimal"}))
    assert get_default_layout(tmp_path) == "minimal"


def test_get_default_layout_none_home():
    assert get_default_layout(None) == "default"
