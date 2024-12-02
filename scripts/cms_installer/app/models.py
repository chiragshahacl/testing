from pydantic import (
    BaseModel,
    IPvAnyAddress,
    ValidationError,
    model_validator,
    FilePath,
    StringConstraints,
    AnyUrl,
)
from typing import Annotated, Optional


class IPAddressesField(BaseModel):
    ip1: IPvAnyAddress

    @staticmethod
    def from_input(value: str) -> bool:
        try:
            IPAddressesField(ip1=value)
        except ValidationError:
            return False
        return True


class K8sClusterConfigContext(BaseModel):
    ip_cp: IPvAnyAddress
    ip1: IPvAnyAddress
    ip2: IPvAnyAddress
    ip3: IPvAnyAddress

    @model_validator(mode="after")
    def check_ip_addresses_match(cls, values):
        if len({values.ip_cp, values.ip1, values.ip2, values.ip3}) < 4:
            raise ValueError("All IP addresses must be different")
        return values


class K8sLoadBalancerConfigContext(BaseModel):
    lb_domain: AnyUrl
    lb_ingress_ip: IPvAnyAddress
    lb_ingress_domain: AnyUrl
    lb_public_key: FilePath
    lb_private_key: FilePath

    @model_validator(mode="after")
    def check_ip_addresses_match(cls, values):
        ips = {
            db.installation_data.k8s_cluster_config.ip_cp,
            db.installation_data.k8s_cluster_config.ip1,
            db.installation_data.k8s_cluster_config.ip2,
            db.installation_data.k8s_cluster_config.ip3,
            values.lb_ingress_ip,
        }
        if len(ips) < 5:
            raise ValueError(
                "The load balancer ingress IP addresses must be different from the ones used for the Kubernetes cluster."
            )
        return values

    @model_validator(mode="after")
    @classmethod
    def check_domains_match(cls, values):
        if values.lb_domain == values.lb_ingress_domain:
            raise ValueError("The domains must be different.")
        return values


UNIX_USERNAME_REGEX = r"^[a-z][-a-z0-9_]*\$?$"


class SSHConfigContext(BaseModel):
    ssh_username: Annotated[
        str,
        StringConstraints(strip_whitespace=True, pattern=UNIX_USERNAME_REGEX),
    ]
    private_key_path: FilePath

    @model_validator(mode="before")
    def validate_private_key_path(cls, values):
        path = values.get("private_key_path")

        if not path.endswith(".pem"):
            raise ValueError("A .pem file must be specified.")

        return values


class DiskConfigContext(BaseModel):
    data_disk_operations_enabled: bool
    data_disk_device_name: Annotated[
        Optional[str], StringConstraints(min_length=1, strip_whitespace=True)
    ]
    data_disk_manually_encrypted: bool
    data_disk_encryption_key: Optional[FilePath] = None

    @model_validator(mode="before")
    @classmethod
    def validate_disk_device_name(cls, values):
        data_disk_operations_enabled = values.get("data_disk_operations_enabled")
        data_disk_device_name = values.get("data_disk_device_name")

        if data_disk_operations_enabled and not data_disk_device_name:
            raise ValueError("The disk device name must be defined.")

        if not data_disk_device_name or not data_disk_operations_enabled:
            values["data_disk_device_name"] = None

        return values

    @model_validator(mode="before")
    @classmethod
    def validate_encryption_key_path_name(cls, values):
        data_disk_manually_encrypted = values.get("data_disk_manually_encrypted")
        data_disk_encryption_key = values.get("data_disk_encryption_key")

        if data_disk_manually_encrypted and not data_disk_encryption_key:
            raise ValueError("The disk encryption key path must be defined.")

        if not data_disk_manually_encrypted:
            values["data_disk_encryption_key"] = None

        return values


class InstallationData(BaseModel):
    ssh_config: Optional[SSHConfigContext] = None
    k8s_cluster_config: Optional[K8sClusterConfigContext] = None
    k8s_lb_config: Optional[K8sLoadBalancerConfigContext] = None
    disk_config: Optional[DiskConfigContext] = None


class Database:
    def __init__(self):
        self.installation_data = InstallationData()


db = Database()
