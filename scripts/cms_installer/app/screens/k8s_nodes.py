from pydantic import ValidationError
from textual.app import ComposeResult
from textual.screen import Screen
from textual.validation import Function
from textual.widgets import Button, Input, Static, Header, Label
from textual.containers import Container, VerticalScroll

from app.models import IPAddressesField, K8sClusterConfigContext, db
from app.screens.k8s_lb import K8sLoadBalancerConfigScreen

CONTROL_PLANE_TEXT = """\
The IPV4 address the control plane VM.
"""
WORKER_TEXT = """\
The IPV4 address for each of the K8s nodes.
"""


class K8sClusterConfigScreen(Screen):
    TITLE = "K8s Nodes Config"
    CSS_PATH = "../styles/common.tcss"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.ip_cp_input = Input(
            placeholder="Control plane IP, e.g., 10.0.0.4",
            validators=[
                Function(
                    IPAddressesField.from_input, "Value is not a valid ip address."
                )
            ],
        )
        self.ip1_input = Input(
            placeholder="First IP, e.g., 10.0.0.4",
            validators=[
                Function(
                    IPAddressesField.from_input, "Value is not a valid ip address."
                )
            ],
        )
        self.ip2_input = Input(
            placeholder="Second IP, e.g., 10.0.0.5",
            validators=[
                Function(
                    IPAddressesField.from_input, "Value is not a valid ip address."
                )
            ],
        )
        self.ip3_input = Input(
            placeholder="Third IP, e.g., 10.0.0.6",
            validators=[
                Function(
                    IPAddressesField.from_input, "Value is not a valid ip address."
                )
            ],
        )
        self.submit_message = Static("")

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="sidebar"):
            yield Label("K8s control plane ip address")
            yield Static(CONTROL_PLANE_TEXT)
            yield Label("K8s worker ip address")
            yield Static(WORKER_TEXT)

        yield Header(id="header")

        with Container(id="app-grid"):
            with VerticalScroll(id="main-zone"):
                yield Label("K8s Control Plane IP address")
                yield self.ip_cp_input
                yield Label("K8s worker 1 Ip address")
                yield self.ip1_input
                yield Label("K8s worker 2 Ip address")
                yield self.ip2_input
                yield Label("K8s worker 3 Ip address")
                yield self.ip3_input
                yield self.submit_message

            with Container(id="buttons-zone"):
                yield Button("Back", id="back-button")
                yield Button("Next", id="next-button")

    def validate_data(self):
        try:
            data = K8sClusterConfigContext(
                ip_cp=self.ip_cp_input.value,
                ip1=self.ip1_input.value,
                ip2=self.ip2_input.value,
                ip3=self.ip3_input.value,
            )
            self.db.installation_data.k8s_cluster_config = data
            self.app.push_screen(K8sLoadBalancerConfigScreen())
        except ValidationError:
            self.submit_message.update(
                "Make sure to enter all different valid ip addresses."
            )

    def on_button_pressed(self, btn: Button.Pressed) -> None:
        if btn.button.id == "back-button":
            self.app.pop_screen()

        if btn.button.id == "next-button":
            self.validate_data()
