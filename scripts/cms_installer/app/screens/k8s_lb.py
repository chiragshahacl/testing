from pydantic import ValidationError
from textual.app import ComposeResult
from textual.screen import Screen
from textual.validation import Function
from textual.widgets import Button, Input, Static, Header, Label
from textual.containers import Container, VerticalScroll

from app.models import IPAddressesField, K8sLoadBalancerConfigContext, db
from app.screens.disk import DiskConfigScreen

CONTROL_PLANE_LB_DOMAIN_TEXT = """\
It defines DNS record for the Kubernetes control-plane Load Balancer. This is the address to be used for the Kubernetes API access. LB_K8S_API_FQDN="cp.<domain>"
"""
LB_INGRESS_IP_TEXT = """\
It defines IP address of the host to be used as a Load Balancer for the workload running in the cluster.
"""

LB_INGRESS_DOMAIN_TEXT = """\
It defines the DNS domain to use for the Central Hub endpoints (e.g., api.${LB_INGRESS_DOMAIN}, web.${LB_INGRESS_DOMAIN}).
"""

LB_DOMAIN_PUBLIC_KEY_TEXT = """\
It defines a name of the public key file for the certificate to be used for the Central Hub endpoints. It should be a full chain of certificates, starting from the leaf certificate and ending with the root CA certificate.
"""

LB_DOMAIN_PRIVATE_KEY_TEXT = """\
It defines a name of the private key file for the certificate to be used for the Central Hub endpoints.
"""


class K8sLoadBalancerConfigScreen(Screen):
    TITLE = "K8s Load Balancer config"
    CSS_PATH = "../styles/common.tcss"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db
        self.control_plane_lb_domain_input = Input(
            placeholder="DNS domain, eg: cp.sibel_health.com"
        )
        self.ip_lb_ingress_input = Input(
            placeholder="Load balancer IP, e.g., 10.0.0.4",
            validators=[
                Function(
                    IPAddressesField.from_input, "Value is not a valid ip address."
                )
            ],
        )
        self.lb_ingress_domain_input = Input(
            placeholder="DNS domain, eg: web.sibel_health.com"
        )
        self.lb_domain_public_key_input = Input()
        self.lb_domain_private_key_input = Input()
        self.submit_message = Static("")

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="sidebar"):
            yield Label("Control Plane Load Balancer")
            yield Static(CONTROL_PLANE_LB_DOMAIN_TEXT)
            yield Label("Load balancer ingress IP")
            yield Static(LB_INGRESS_IP_TEXT)
            yield Label("Load balancer ingress domain")
            yield Static(LB_INGRESS_DOMAIN_TEXT)
            yield Label("Load Balancer domain public key")
            yield Static(LB_DOMAIN_PUBLIC_KEY_TEXT)
            yield Label("Load Balancer domain private key")
            yield Static(LB_DOMAIN_PRIVATE_KEY_TEXT)

        yield Header(id="header")

        with Container(id="app-grid"):
            with VerticalScroll(id="main-zone"):
                yield Label("Control Plane Load Balancer")
                yield self.control_plane_lb_domain_input
                yield Label("Load balancer ingress IP")
                yield self.ip_lb_ingress_input
                yield Label("Load balancer ingress domain")
                yield self.lb_ingress_domain_input
                yield Label("Load Balancer domain public key")
                yield self.lb_domain_public_key_input
                yield Label("Load Balancer domain private key")
                yield self.lb_domain_private_key_input

                yield self.submit_message

            with Container(id="buttons-zone"):
                yield Button("Back", id="back-button")
                yield Button("Next", id="next-button")

    def validate_data(self):
        try:
            data = K8sLoadBalancerConfigContext(
                lb_domain=self.control_plane_lb_domain_input.value,
                lb_ingress_ip=self.ip_lb_ingress_input.value,
                lb_ingress_domain=self.lb_ingress_domain_input.value,
                lb_public_key=self.lb_domain_public_key_input.value,
                lb_private_key=self.lb_domain_private_key_input.value,
            )
            self.db.installation_data.k8s_lb_config = data
            self.app.push_screen(DiskConfigScreen())
        except ValidationError as e:
            self.submit_message.update(f"Errors: {e}")

    def on_button_pressed(self, btn: Button.Pressed) -> None:
        if btn.button.id == "back-button":
            self.app.pop_screen()

        if btn.button.id == "next-button":
            self.validate_data()
