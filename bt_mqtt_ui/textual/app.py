from os import getenv
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.reactive import var
from textual.widgets import Footer, Header, Placeholder


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

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def compose(self) -> ComposeResult:
        """A minimal screen of all other screen have been closed"""
        yield Header()
        yield Placeholder()
        yield Footer()

    def on_mount(self):
        pass


def run():
    app = MQTTApp()
    app.run()


if __name__ == "__main__":
    run()
