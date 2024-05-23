from bt_mqtt_ui.textual.config import AppConfig


def test_config_new():
    """Test that the app config can be initialized with all defaults without any validation error"""
    cfg = AppConfig()
    assert cfg.to_yaml()
