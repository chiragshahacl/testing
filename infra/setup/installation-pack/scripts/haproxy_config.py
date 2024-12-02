from jinja2 import Environment, FileSystemLoader
import os

control_plane_count = int(os.environ.get("K8S_CLUSTER_CONTROL_HOSTS"))
k8s_cluster_ips = os.environ.get("K8S_CLUSTER_IPS")
k8s_cluster_ips = k8s_cluster_ips.split(" ")

ingress_backend_ips = k8s_cluster_ips[control_plane_count:]
k8s_api_backend_ips = k8s_cluster_ips[:control_plane_count]

loki_password_hash = os.environ.get("LOKI_PASSWORD_HASH")

def render_haproxy_cfg(kind, services):
    env = Environment(loader=FileSystemLoader ('haproxy'), trim_blocks=True)
    templ = env.get_template('_haproxy.jinja2.cfg')
    outp = templ.render(services=services, loki_password_hash=loki_password_hash)
    if kind == "k8s":
        with open('haproxy/api-haproxy.cfg', 'w') as f:
            f.write(outp)
    elif kind == "ingress":
        with open('haproxy/ingress-haproxy.cfg', 'w') as f:
            f.write(outp)
    elif kind == "combined":
        with open('haproxy/combined-haproxy.cfg', 'w') as f:
            f.write(outp)

ingress_backends = [
    {
        "name": "ingress",
        "port":80,
        "backend_port":32080,
        "backends": ingress_backend_ips
    },
    {
        "name": "ingress",
        "port":443,
        "backend_port":32443,
        "backends": ingress_backend_ips
    },
    {
        "name": "ingress",
        "port":6661,
        "backend_port":32661,
        "backends": ingress_backend_ips
    }
]

k8s_api_backends = [
    {
        "name": "k8s-api",
        "port":6443,
        "backend_port":6443,
        "backends": k8s_api_backend_ips
    },
    {
        "name": "rke-server",
        "port":9345,
        "backend_port":9345,
        "backends": k8s_api_backend_ips
    }
]

loki_backends = [
    {
        "name": "loki",
        "port":3100,
        "backend_port":32333,
        "backends": ingress_backend_ips
    },
]
render_haproxy_cfg("combined", ingress_backends + k8s_api_backends + loki_backends)