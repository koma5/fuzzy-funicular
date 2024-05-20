from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    RichLog,
    Placeholder,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual.containers import Grid, Vertical
from textual.widget import Widget
from textual.reactive import var, reactive

from bt_mqtt_ui.models.device_state import DeviceState
from bt_mqtt_ui.models.device_telemetry import DeviceTelemetry
from bt_mqtt_ui.models.tasmota_discovery import MQTTDiscovery
from bt_mqtt_ui.textual.config import AppConfig, load_config


class DeviceContainer(Grid):
    pass


class Terminal(RichLog):
    """Terminal Widget"""

    hidden: var[bool] = var(False)

    def watch_hidden(self):
        # TODO
        pass


class DeviceTitle(Widget):
    """A widget to render a title together with online status"""

    OFFLINE_EMOJI = ":red_circle:"
    ONLINE_EMOJI = ":green_circle:"

    is_online: reactive[bool] = True
    device_id: reactive[str] = reactive("")

    def render(self):
        mapping = {True: self.ONLINE_EMOJI, False: self.OFFLINE_EMOJI}
        return f"{mapping[self.is_online]} {self.device_id}"


class DevicePanel(Vertical):
    """Panel container for every device"""

    device_id: reactive[str] = reactive("Unknown Device ID")

    def compose(self):
        yield DeviceTitle().data_bind(device_id=self.device_id)

    def update(self, data):
        raise NotImplementedError()


topic_rgx_to_models = {
    r"tele/\w+/STATE": DeviceState,
    r"tele/\w+/SENSOR": DeviceTelemetry,
    r"tasmota/discovery/\w+/config": MQTTDiscovery,
}


class MQTTApp(App):
    """Textual app integrating alot of cool building blocks"""

    TITLE = "MQTT TUI"
    SUB_TITLE = f"Version ???"
    BINDINGS = [
        ("d", "toggle_dark", "DarkMode"),
        ("q", "quit", "Quit App"),
    ]

    CSS_PATH = "styles.tcss"
    COMMANDS = App.COMMANDS

    # reactive vars can be dynamic when using a function
    config: var[AppConfig] = var(load_config)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def create_terminal(self):
        """Create the terminal widget using the config"""
        t = Terminal(name="Terminal")
        t.styles.bg_color = self.config.terminal.style.bg_color
        return t

    def compose(self) -> ComposeResult:
        """A minimal screen of all other screen have been closed"""
        yield Header()
        with TabbedContent(initial="status"):
            with TabPane("Status", id="status"):
                with DeviceContainer():
                    yield DevicePanel()
                    yield DevicePanel()
            with TabPane("Plots", id="plots"):
                yield Placeholder("Here be one plot")
            with TabPane("Config"):
                yield TextArea(self.config.to_yaml(), language="yaml")
        yield self.create_terminal()
        yield Footer()

    def on_mount(self):
        pass

    @property
    def device_container(self):
        return self.query_one(DeviceContainer)

    @property
    def terminal(self):
        return self.query_one(Terminal)

    def write_to_terminal(self, renderable):
        self.terminal.write(content=renderable)

    @staticmethod
    def device_id_from_topic(topic) -> str:
        """Extracts device id from topic"""
        return topic.split("/")[-2]

    def _on_mqtt_message(self, topic: str, message: dict):
        if topic.startswith("tasmota"):
            # TODO What is really returned here?
            # resp = MQTTDiscovery()
            return
        try:
            device_id = self.device_id_from_topic(topic)
            if topic.endswith("STATE"):
                self._on_update_state(device_id, DeviceState.model_validate(message))
            elif topic.endswith("SENSOR"):
                self._on_update_telemetry(
                    device_id, DeviceTelemetry.model_validate(message)
                )
        except Exception as e:
            self.write_to_terminal(str(e))

    def _on_update_state(self, device_id, mqtt_data: DeviceState):
        """State message handling for topic STATE"""
        pass

    def _on_update_telemetry(self, device_id, mqtt_data: DeviceTelemetry):
        """Handle device data and update plots"""
        pass

    def update_device(self, device_id, data: DeviceState):
        panel = self.device_container.query_one(device_id, expect_type=DevicePanel)
        if not panel:
            return
        panel.update(data)

    def mount_device(self, device_id: str):
        parent = self.device_container
        panel = parent.query_one(device_id)
        if panel:
            return
        panel = DevicePanel(id=device_id)
        parent.mount(panel)


def run():
    app = MQTTApp()
    app.run()


if __name__ == "__main__":
    run()
