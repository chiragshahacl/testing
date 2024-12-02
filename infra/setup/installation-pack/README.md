
## Prerequisites
### VMs requirements
* 1 VM for container registry
    * OS: Ubuntu 22.04
    * OS disk: 50GB minimum
    * 2 CPU cores
    * 4GB RAM

* 1 Loadbalancer VM for controlplane
    * OS: Ubuntu 22.04
    * OS disk: 30GB minimum
    * 2 CPU cores
    * 4GB RAM

* 1 Loadbalancer VM for workload
    * OS: Ubuntu 22.04
    * OS disk: 30GB minimum
    * 2 CPU cores
    * 4GB RAM

* 1 Control plane VM
    * OS: Ubuntu 22.04
    * OS disk: 50GB minimum
    * 2 CPU cores
    * 4GB RAM

* 3 worker VMs
    * OS: Ubuntu 22.04
    * OS disk: 50GB minimum
    * DATA disk 300GB minimum
    * 8 CPU cores
    * 8GB RAM

### VMs preparations
1. All VMs should be provisioned and accessible from the machine that will run the installation process and the connection can be established via SSH using SSH key. The user who connects to the VMs requires sudo access with no password.

2. Mount DATA disk on all worker VMs as /opt/local-path-provisioner/
    1) **Identify the Disk:**
       - Run `lsblk` or `fdisk -l` to list all disks and identify the new disk (e.g., `/dev/sdb`, `/dev/sdc`, etc.).
    
    2) **Partition the Disk (if needed):**
       - Run `sudo fdisk /dev/[your-disk]`.
       - Press `n` for a new partition, select the type, and follow prompts.
       - Press `w` to write changes and exit.
    
    3) **Create a Filesystem:**
       - Use `sudo mkfs.ext4 /dev/[your-partition]` (e.g., `/dev/sdb1`).
    
    4) **Create a Mount Point:**
       - Run `sudo mkdir -p /opt/local-path-provisioner/`.
    
    5) **Mount the Disk:**
       - Execute `sudo mount /dev/[your-partition] /opt/local-path-provisioner/`.
    
    6) **Configure Mount at Boot (Optional):**
       - Open `/etc/fstab` using `sudo nano /etc/fstab`.
       - Add a line like:
         ```
         /dev/[your-partition] /opt/local-path-provisioner/ ext4 defaults 0 2
         ```
       - Replace `[your-partition]` (e.g., `/dev/sdb1`) and save.
    
    7) **Verify Mount:**
       - Run `df -h` to check if `/opt/local-path-provisioner/` shows the mounted disk and its size.

### Install preparations
1. Make sure the `docker` is installed on the machine that will run the installation process
2. Review `.env.example` file and create your own file `.env` with appropriate values for the installation and make sure it is in the current working directory (the directory from which the installation will be executed)
3. Prepare Patient Monitor certificates and make sure it is in the current working directory (the directory from which the installation will be executed):
    * consumerLeaf1.key
    * consumerLeaf1.crt
    * intermediateCA.crt
4. Make sure the private SSH key for the VMs is in the current working directory (the directory from which the installation will be executed)
5. Make sure that DNS records for `${LB_K8S_API_FQDN}`, `${REGISTRY_FQDN}`, `api.${LB_INGRESS_DOMAIN}` and `cms.${LB_INGRESS_DOMAIN}` are set accordingly.
```
${REGISTRY_FQDN} name should be set to ${REGISTRY_IP}
${LB_K8S_API_FQDN} name should be set to ${LB_INGRESS_IP}
api.${LB_INGRESS_DOMAIN} name should be set to ${LB_INGRESS_IP}
cms.${LB_INGRESS_DOMAIN} name should be set to ${LB_INGRESS_IP}
```
6. Pull the container image `install:0.1.0`


### Installation
1. Run `docker run -it -v $(pwd):/tmp install:0.1.0`. The command will start the container image with installation tasks and mount the current working directory with prepared SSH private key, `.env` file and the PM certificates into the `/tmp` folder.  
Please make sure that the current workind directory has the files listed above.
2. Run the installation task as following:
```
task 10-install-all
```

This command utilizes the `Taskfile` utility and will run a set of subtasks to configure Load Balancers, setup a Kubernetes cluster and then deploy required components for the Central Hub.