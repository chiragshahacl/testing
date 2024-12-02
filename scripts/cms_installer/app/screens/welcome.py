from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Label, Footer
from textual.containers import Center, Container
from app.screens.ssh_config import SSHConfigScreen


class WelcomeScreen(Screen):
    CSS_PATH = "../styles/welcome.tcss"

    def compose(self) -> ComposeResult:
        yield Container(
            Center(
                Label(
                    "Welcome to Central Server installer \n The Installer will guide you through the installation process.",
                    classes="welcome-message",
                ),
                Label("Please click any button to continue", id="click-instruction"),
            ),
            id="content-container",
        )

        yield Label("© 2024 Sibel Health, Inc", classes="centered-footer")
        yield Label("Version 2.0.0.alpha.3", classes="centered-footer")
        yield Footer()

    def on_key(self, event) -> None:
        self.app.push_screen(SSHConfigScreen())
