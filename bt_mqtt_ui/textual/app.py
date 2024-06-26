import json
import re

from rich.console import RenderableType
from textual.app import App, ComposeResult, RenderResult
from textual.css.query import NoMatches
from textual.widgets import (
    Footer,
    Header,
    Label,
    TabbedContent,
    TabPane,
    Placeholder,
    TextArea
)
from textual.widget import Widget
from textual.containers import Grid, Container
from textual.reactive import var, reactive
from textual import on

from bt_mqtt_ui.models.device_state import DeviceState
from bt_mqtt_ui.models.device_telemetry import DeviceTelemetry
from bt_mqtt_ui.models.tasmota_discovery import MQTTDiscovery
from bt_mqtt_ui.textual.config import AppConfig, load_config
from bt_mqtt_ui.textual.widgets import MqttClientWidget, Terminal


def device_id_from_topic(topic) -> str:
    """Extracts device id from topic"""
    return topic.split("/")[-2]


class DeviceContainer(Grid):
    pass


class DeviceTitle(Widget):
    """A widget to render a title together with online status"""

    DEFAULT_CSS = """
    DeviceTitle {
        width: auto;
        height: auto;
    }
    """

    OFFLINE_EMOJI = ":red_circle:"
    ONLINE_EMOJI = ":green_circle:"
    icon_mapping = {True: ONLINE_EMOJI, False: OFFLINE_EMOJI}

    is_online: reactive[bool] = reactive(True)
    device_id: reactive[str] = reactive("Unknown Device ID")

    def render(self) -> RenderResult:
        return f"{self.icon_mapping[self.is_online]} {self.device_id}"


class KeyValue(Label):

    def __init__(
        self,
        key: str,
        renderable: RenderableType = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__(
            renderable=renderable,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.key = key

    value: reactive[str] = reactive("")

    def render(self):
        if self.value:
            return f"{self.key}: {self.value}"
        return ""


class DevicePanel(Container):
    """Panel container for every device"""

    device_id: reactive[str] = reactive("Unknown Device ID")
    ip: var[str] = var("")
    device_name: var[str] = var("")
    host_name: var[str] = var("")
    is_online: reactive[bool] = reactive(True)

    def compose(self):
        with Container(classes="panel-header"):
            # TODO: This binding does not work
            # It works with query_one
            yield DeviceTitle().data_bind(
                device_id=self.device_id, is_online=self.is_online
            )
        with Container(classes="panel-content"):
            yield KeyValue(key="HOSTNAME").data_bind(value=self.host_name)
            yield KeyValue(key="DN").data_bind(value=self.device_name)
            yield KeyValue(key="IP").data_bind(value=self.ip)

    def update(self, data: DeviceTelemetry):
        raise NotImplementedError()


class MQTTApp(App):
    """Textual app integrating alot of cool building blocks"""

    TITLE = "MQTT TUI"
    SUB_TITLE = f"Version ???"
    BINDINGS = [
        ("d", "toggle_dark", "DarkMode"),
        ("t", "toggle_terminal", "Toggle Terminal"),
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
        t = Terminal(name="Terminal", id="term", classes="hidden")
        t.styles.bg_color = self.config.terminal.style.bg_color
        return t

    def compose(self) -> ComposeResult:
        """A minimal screen of all other screen have been closed"""
        yield Header()
        with TabbedContent(initial="status"):
            with TabPane("Status", id="status"):
                yield DeviceContainer()
            with TabPane("MQTT", id="mqtt-term"):
                yield MqttClientWidget(
                    host=self.config.mqtt.connection.host,
                    port=self.config.mqtt.connection.port,
                    topics=self.config.mqtt.subscriptions,
                    clear_on_n_msgs=100,
                )
            with TabPane("Plots", id="plots"):
                yield Placeholder("Here be one plot")
            with TabPane("Config"):
                yield TextArea(self.config.to_yaml(), read_only=True, language="yaml")
        yield self.create_terminal()
        yield Footer()

    def on_mount(self):
        pass

    def handler_for_topic(self, topic):
        topic_rgx_to_fns = {
            r"tele/\w+/STATE": self._on_update_state,
            r"tele/\w+/SENSOR": self._on_update_telemetry,
            r"tasmota/discovery/\w+/config": self._on_update_discovery,
            r"tele/\w+/LWT": self._on_last_will_topic,
        }
        for rgx, fn in topic_rgx_to_fns.items():
            m = re.search(rgx, topic)
            if m:
                return fn

    @property
    def device_container(self):
        return self.query_one(DeviceContainer)

    @property
    def terminal(self):
        return self.query_one("#term", Terminal)

    def write_to_terminal(self, renderable):
        self.terminal.write(content=renderable)

    def action_toggle_terminal(self):
        self.terminal.toggle_class("hidden")

    def _on_update_state(self, msg: MqttClientWidget.MQTTMessage):
        """State message handling for topic STATE"""
        device_id = device_id_from_topic(msg.topic)
        model = DeviceState.model_validate(json.loads(msg.payload))

    def _on_update_telemetry(self, msg: MqttClientWidget.MQTTMessage):
        """Handle device data and update plots"""
        device_id = device_id_from_topic(msg.topic)
        model = DeviceTelemetry.model_validate(json.loads(msg.payload))

    def _on_update_discovery(self, msg: MqttClientWidget.MQTTMessage):
        model = MQTTDiscovery.model_validate(json.loads(msg.payload))
        self.mount_device(model.t, model)

    def _on_last_will_topic(self, msg: MqttClientWidget.MQTTMessage):
        device_id = device_id_from_topic(msg.topic)
        panel = self.get_panel_from_device_id(device_id)
        if not panel:
            self.write_to_terminal(
                f"Topic: {msg.topic} - Set online state: Could not find panel with id {device_id}"
            )
            return
        panel.is_online = msg.payload == "Online"

    def update_device(self, device_id, data: DeviceTelemetry):
        panel = self.get_panel_from_device_id(device_id)
        if not panel:
            return
        panel.update(data)

    def get_panel_from_device_id(self, device_id: str):
        try:
            panel = self.device_container.query_one(f"#{device_id}", DevicePanel)
        except NoMatches:
            return None
        return panel

    def mount_device(self, device_id: str, config: MQTTDiscovery):
        panel = self.get_panel_from_device_id(device_id)
        if panel:
            return
        parent = self.device_container
        panel = DevicePanel(id=device_id)
        panel.host_name = config.hn
        panel.device_id = device_id
        parent.mount(panel)
        panel.ip = config.ip
        panel.device_name = config.dn
        panel.is_online = True

    @on(MqttClientWidget.MQTTMessage)
    def on_mqtt_message(self, msg: MqttClientWidget.MQTTMessage):
        """Listener for events bubbled up by the Widget. Place to handle graphs and plot updated"""
        handler_fn = self.handler_for_topic(msg.topic)
        if not handler_fn:
            self.write_to_terminal(f"Ignoring message for topic '{msg.topic}'")
            return
        handler_fn(msg)


def run():
    app = MQTTApp()
    app.run()


if __name__ == "__main__":
    run()
