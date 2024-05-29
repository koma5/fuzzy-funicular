# BT MQTT UI

- Tasmota Device Discovery
- Textual TUI for Device control

## Config

Place a config called `bt_mqtt_ui_config.yml` in path where you start the app. You can also set the config path via env var:

    export BT_UI_CONFIG=<path/to/config>

Examples config:

```yaml
mqtt:
  connection: 
    host: 127.0.0.1
    port: 1883
  subscriptions:
    - "tasmota/discovery/+/+"
    - "tele/+/+"
```

## Development

### Poetry installation

If you have never working with poetry, it is a python build tool that allows for easier dependency management und dependence updates, 
automatic creation of virtual envs. It's best to install `poetry` as a **global tool** on your machine not specific to project. 
It's [recommended](https://python-poetry.org/docs/) to install it with [pipx](https://pipx.pypa.io/latest/installation/).

### Getting started

    # Install all dependencies incl. dev
    poetry install

    # with venv
    python3 -m venv .venv
    source .venv/bin/activate && pip install -r requirements.txt

### Running in dev mode

    # As described in textual docs
    textual run --dev bt_mqtt_ui/textual/app.py

    # or use provided script
    ./run_dev.sh

### Running without dev option

    # Using the entrypoint in pyproject.toml 'tool.poetry.scripts'
    poetry run bt-mqtt-ui

    # or when installed e.g. with pipx as global package
    bt-mqtt-ui

### Create models

Via the tool `datamodel-codegenerator`, bootstrap pydantic classes can be generated to speed up implementing mqtt data messages.

    datamodel-codegen --output bt_mqtt_ui/models/tasmota_discovery.py --input tasmota_discovery_C44F33D288A1_config.txt --input-file-type json --class-name MQTTDiscovery --target-python-version 3.10

    datamodel-codegen --output bt_mqtt_ui/models/device_state.py --input tele_tasmota_CE1412_STATE.txt  --input-file-type json --class-name DeviceState --target-python-version 3.10

    datamodel-codegen --output bt_mqtt_ui/models/device_telemetry.py --input tele_tasmota_CEE97F_SENSOR.txt --input-file-type json --class-name DeviceTelemetry --target-python-version 3.10

### Create `requirements.txt`

    poetry export -o requirements.txt --without-hashes
