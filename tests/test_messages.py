import pytest

from bt_mqtt_ui.models.device_telemetry import DeviceTelemetry
from bt_mqtt_ui.models.tasmota_discovery import MQTTDiscovery


@pytest.mark.parametrize("file", ("tele_tasmota_CEE97F_SENSOR.txt",))
def test_telemetry_msg(file, test_data_message):
    model = DeviceTelemetry.model_validate(test_data_message(file))


@pytest.mark.parametrize("file", ("tasmota_discovery_1.txt",))
def test_discovery_msg(file, test_data_message):
    model = MQTTDiscovery.model_validate(test_data_message(file))
