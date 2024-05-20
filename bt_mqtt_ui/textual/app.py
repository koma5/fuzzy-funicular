from textual.app import App, ComposeResult
from textual.widgets import (
    Footer,
    Header,
    RichLog,
    Placeholder,
    Static,
    Label,
    TabbedContent,
    TabPane,
    TextArea
)
from textual.containers import Grid, Vertical
from textual.reactive import var

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


class DevicePanel(Vertical):
    """Panel container for every device"""

    device_id: var[str] = var("Unknown Device ID")

    def watch_device_id(self, old, new_device_id: str):
        if new_device_id:
            self.styles.border_title = new_device_id

    def compose(self):
        # TODO: bind values to sub widget: yield Widget().data_bind(time=Panel.cfg.widget_cfg)
        yield Label(self.device_id)
        yield Static("Online Status")
        yield Static("Turn on/off")

    def update(self, mqtt_data: DeviceState):
        pass


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
            with TabPane("Graphs", id="graphs"):
                yield Placeholder("Here you be one graph")
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

    def add_config(self, config: AppConfig):
        self.config = config


def run():
    app = MQTTApp()
    app.run()


if __name__ == "__main__":
    run()
