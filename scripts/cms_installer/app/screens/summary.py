from textual.app import ComposeResult
from textual.containers import Center, Container
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from app.models import db


class SummaryScreen(Screen):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.db = db

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            yield Static(
                f"SSH config: {self.db.installation_data.ssh_config.ssh_username}, {self.db.installation_data.ssh_config.private_key_path}"
            )
            yield Static(
                f"The ip addresses are: "
                f"cp {self.db.installation_data.k8s_cluster_config.ip_cp} "
                f"node 1: {self.db.installation_data.k8s_cluster_config.ip1} and "
                f"node 2: {self.db.installation_data.k8s_cluster_config.ip2} and "
                f"node 3: {self.db.installation_data.k8s_cluster_config.ip3}"
            )
            yield Static(
                f"K8s load balancer: "
                f"{self.db.installation_data.k8s_lb_config.lb_domain} "
                f"{self.db.installation_data.k8s_lb_config.lb_ingress_ip} "
                f"{self.db.installation_data.k8s_lb_config.lb_ingress_domain} "
                f"{self.db.installation_data.k8s_lb_config.lb_public_key} "
                f"{self.db.installation_data.k8s_lb_config.lb_private_key}"
            )
            yield Static(
                f"Disk config: "
                f"{self.db.installation_data.disk_config.data_disk_operations_enabled} "
                f"{self.db.installation_data.disk_config.data_disk_device_name} "
                f"{self.db.installation_data.disk_config.data_disk_manually_encrypted} "
                f"{self.db.installation_data.disk_config.data_disk_encryption_key} "
            )

        with Container(id="buttons-zone"):
            yield Button("Back", id="back-button")

        yield Footer()

    def on_button_pressed(self, btn: Button.Pressed) -> None:
        if btn.button.id == "back-button":
            self.app.pop_screen()
