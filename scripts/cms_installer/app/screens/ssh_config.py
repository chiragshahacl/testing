from pydantic import ValidationError
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Static, Label, Header
from textual.containers import Container, VerticalScroll

from app.models import SSHConfigContext, db
from app.screens.k8s_nodes import K8sClusterConfigScreen


PRIVATE_KEY_PATH_TEXT = """\
This variable defines a name of the SSH private key to be used for the connection to various components' nodes during the install process. Should be in ".pem" format.
"""
USERNAME_TEXT = """\
This variable defines which is the SSH user to be used for the connection to various components' nodes during the install process.
"""


class SSHConfigScreen(Screen):
    TITLE = "SSH Config"
    CSS_PATH = "../styles/common.tcss"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.ssh_user_input = Input(placeholder="SSH username, eg: ubuntu")
        self.private_key_path = Input(placeholder="Private key path")
        self.submit_message = Static("")

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="sidebar"):
            yield Label("Username")
            yield Static(USERNAME_TEXT)
            yield Label("Private Key")
            yield Static(PRIVATE_KEY_PATH_TEXT)

        yield Header(id="header")

        with Container(id="app-grid"):
            with VerticalScroll(id="main-zone"):
                yield Label("Username")
                yield self.ssh_user_input
                yield Label("Private Key Path")
                yield self.private_key_path
                yield self.submit_message

            with Container(id="buttons-zone"):
                yield Button("Next", id="next-button")

    def validate_data(self):
        try:
            data = SSHConfigContext(
                ssh_username=self.ssh_user_input.value,
                private_key_path=self.private_key_path.value,
            )
            self.db.installation_data.ssh_config = data
            self.app.push_screen(K8sClusterConfigScreen())
        except ValidationError as e:
            self.submit_message.update(
                f"Make sure to input valid username and private key name: {e}"
            )

    def on_button_pressed(self, btn: Button.Pressed) -> None:
        if btn.button.id == "next-button":
            self.validate_data()
