from textual.app import App, ComposeResult, RenderResult
from textual.widgets import (
    Footer,
    Header,
    RichLog,
    Label,
    TabbedContent,
    TabPane,
    Placeholder,
    TextArea,
)
from textual.containers import Grid, Vertical, Container
from textual.reactive import var, reactive

from bt_mqtt_ui.models.device_state import DeviceState
from bt_mqtt_ui.models.device_telemetry import DeviceTelemetry
from bt_mqtt_ui.models.tasmota_discovery import MQTTDiscovery
from bt_mqtt_ui.textual.config import AppConfig, load_config


def device_id_from_topic(topic) -> str:
    """Extracts device id from topic"""
    return topic.split("/")[-2]


class DeviceContainer(Grid):
    pass


class Terminal(RichLog):
    """Terminal Widget"""

    hidden: var[bool] = var(False)

    def watch_hidden(self):
        # TODO
        pass


class DeviceTitle(Label):
    """A widget to render a title together with online status"""

    OFFLINE_EMOJI = ":red_circle:"
    ONLINE_EMOJI = ":green_circle:"

    is_online: reactive[bool] = reactive(True)
    device_id: reactive[str] = reactive("Unknown Device ID")

    def render(self) -> RenderResult:
        mapping = {True: self.ONLINE_EMOJI, False: self.OFFLINE_EMOJI}
        return f"{mapping[self.is_online]} {self.device_id}"


class DeviceIP(Label):
    ip: reactive[str] = reactive("")

    def render(self) -> RenderResult:
        return f"IP: {self.ip}"


class DevicePanel(Container):
    """Panel container for every device"""

    device_id: reactive[str] = reactive("Unknown Device ID")
    ip: var[str] = var("???")
    is_online: var[bool] = var(True)

    def compose(self):
        with Container(classes="panel-header"):
            yield DeviceTitle().data_bind(
                device_id=self.device_id, is_online=self.is_online
            )
        with Container(classes="panel-content"):
            yield DeviceIP().data_bind(ip=self.ip)

    def update(self, data: DeviceTelemetry):
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
                    yield DevicePanel()
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

    def _on_mqtt_message(self, topic: str, message: dict):
        # TODO use overload functions using different message inputs
        if topic.startswith("tasmota"):
            device_id = device_id_from_topic(topic)
            self.mount_device(device_id, MQTTDiscovery.model_validate(message))
        try:
            device_id = device_id_from_topic(topic)
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

    def update_device(self, device_id, data: DeviceTelemetry):
        panel = self.device_container.query_one(device_id, expect_type=DevicePanel)
        if not panel:
            return
        panel.update(data)

    def mount_device(self, device_id: str, config: MQTTDiscovery):
        parent = self.device_container
        panel = parent.query_one(device_id)
        if panel:
            panel.ip = config.ip
            return
        panel = DevicePanel(id=device_id)
        panel.ip = config.ip
        parent.mount(panel)

    def mark_device_offline(self, device_id: str):
        elem = self.device_container.query_one(device_id, DevicePanel)
        elem.is_online = False


def run():
    app = MQTTApp()
    app.run()


if __name__ == "__main__":
    run()
