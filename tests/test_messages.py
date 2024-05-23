import pytest

from bt_mqtt_ui.models.device_telemetry import DeviceTelemetry


@pytest.mark.parametrize("file", ("tele_tasmota_CEE97F_SENSOR.txt",))
def test_telemetry_msg(file, test_data_message):
    model = DeviceTelemetry.model_validate(test_data_message(file))
