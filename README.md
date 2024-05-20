# BT MQTT UI

- Tasmota Device Discovery
- Textual TUI for Device control

## Development

    poetry run textual run --dev bt_mqtt_ui/textual/app.py

### Create models

    datamodel-codegen --output bt_mqtt_ui/models/tasmota_discovery.py --input tasmota_discovery_C44F33D288A1_config.txt --input-file-type json --class-name MQTTDiscovery --target-python-version 3.10

    datamodel-codegen --output bt_mqtt_ui/models/device_state.py --input tele_tasmota_CE1412_STATE.txt  --input-file-type json --class-name DeviceState --target-python-version 3.10

    datamodel-codegen --output bt_mqtt_ui/models/device_telemetry.py --input tele_tasmota_CEE97F_SENSOR.txt --input-file-type json --class-name DeviceTelemetry --target-python-version 3.10

### Create `requirements.txt`

    poetry export -o requirements.txt --without-hashes