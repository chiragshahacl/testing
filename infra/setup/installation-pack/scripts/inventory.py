from jinja2 import Environment, FileSystemLoader
import os

control_plane_count = int(os.environ.get("K8S_CLUSTER_CONTROL_HOSTS"))
k8s_cluster_ips = os.environ.get("K8S_CLUSTER_IPS")
k8s_cluster_ips = k8s_cluster_ips.split(" ")
lb_ingress_ip = os.environ.get("LB_INGRESS_IP")

masters_ips = k8s_cluster_ips[:control_plane_count]
workers_ips = k8s_cluster_ips[control_plane_count:]
docker_ips = [lb_ingress_ip]

def render_ansible_inventory(kind, hosts):
    env = Environment(loader=FileSystemLoader ('ansible'), trim_blocks=True)
    templ = env.get_template('_inventory.jinja2.ini')
    outp = templ.render(hosts=hosts)
    if kind == "docker":
        with open('ansible/docker-inventory.ini', 'w') as f:
            f.write(outp)
    elif kind == "k8s":
        with open('ansible/k8s-inventory.ini', 'w') as f:
            f.write(outp)

docker_hosts = {
    "docker": docker_ips
}

k8s_hosts = {
    "masters": masters_ips,
    "workers": workers_ips
}

render_ansible_inventory("docker", docker_hosts)
render_ansible_inventory("k8s", k8s_hosts)