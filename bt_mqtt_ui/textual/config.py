from os import getenv
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field

CONFIG_ENV_VAR = "BT_UI_CONFIG"
DEFAULT_CONFIG_PATH = "bt_mqtt_ui_config.yml"


def get_config_path():
    return Path(getenv(CONFIG_ENV_VAR, DEFAULT_CONFIG_PATH))


def load_config():
    cfg_path = get_config_path()
    if cfg_path.is_file():
        return AppConfig(**yaml.safe_load(cfg_path.read_text(encoding="utf-8")))
    else:
        print(f"Config file {cfg_path} not found. You can set the config with env '{CONFIG_ENV_VAR}'")
        return AppConfig()


class MQTTConnection(BaseModel):
    host: str = "127.0.0.1"
    port: int = 1883


class MQTTConfig(BaseModel):
    connection: MQTTConnection = Field(default_factory=MQTTConnection)
    subscriptions: tuple[str] = ("tasmota/discovery/+/+", "tele/+/+")


class TerminalStyle(BaseModel):
    bg_color: str = "black"


class TerminalConfig(BaseModel):
    style: TerminalStyle = Field(default_factory=TerminalStyle)
    dump_config: bool = True


class AppConfig(BaseSettings):
    """Config for textual interface"""
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    terminal: TerminalConfig = Field(default_factory=TerminalConfig)

    def to_yaml(self):
        return yaml.safe_dump(
            self.model_dump(mode="json", exclude_none=True),
            sort_keys=False,
        )
