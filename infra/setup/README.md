## Table of Contents

* [General info about Central Hub deployment](#general-info-about-central-hub-deployment)
* [Central Hub deployment failures during the installation process](#central-hub-deployment-failures-during-the-installation-process)
  * [DNS resolution errors during the installation](#dns-resolution-errors-during-the-installation)
* [How to access K8 dashboard](#how-to-access-k8-dashboard)
* [Central Hub is mulfunctioning](#central-hub-is-mulfunctioning)
* [Central Hub URL is not accessible](#central-hub-url-is-not-accessible)
* [Patient Monitor is not able to connect to the Central Hub](#patient-monitor-is-not-able-to-connect-to-the-central-hub)
* [Connection issues between the pods in the cluster while pods are running on the different nodes](#connection-issues-between-the-pods-in-the-cluster-while-pods-are-running-on-the-different-nodes)
* [Cluster IP addresses change after the reboot of the server](#cluster-ip-addresses-change-after-the-reboot-of-the-server)
* [PostgreSQL database backup](#postgresql-database-backup)
* [PostgreSQL database restore](#postgresql-database-restore)


### General info about Central Hub deployment

A deployment of the Central Hub to a hospital environment is delivered via a 'wrapper' container image (also known as an installation image) that contains all the required components of the Central Hub as gzipped and archived images.

The installation image has 2 flavors - `online` installation (meaning that the target servers are connected to the public internet), and `offline` installation (for cases where the target servers are not connected to the public internet). The `offline` image, in addition to the Central Hub images, also contains 'infrastructure' images (also gzipped and archived) that are required to run the Kubernetes cluster's auxiliary components and the cluster itself.

The installation process is orchestrated using the Taskfile utility (https://taskfile.dev/usage/).
The Taskfile tasks are divided into several subtasks:
* load balancer setup and configuration
* K8S cluster setup
* deploy of K8S auxiliary components
* deploy of Central Hub components

During the installation, the archived images are copied to the target machines to the specified location (`/var/lib/rancher/rke2/agent/images/`) on each machine, unarchived and uploaded to the K8S container runtime. After installation, the copied images are removed from the machines to free up space.

The installation process creates a `kubeconfig` file, which is important for further communication with the deployed K8S cluster. 
The `kubeconfig` file is a configuration file used by the Kubernetes command line tool `kubectl` to authenticate to a Kubernetes cluster, it contains information such as the cluster address, authentication credentials, etc. 
**The `kubeconfig` file should be kept securely, as it provides full administrative access to the cluster.**

The `kubeconfig` file can be found in the same local directory where the installation image was run.  It is not necessary to re-run the installation image after the initial installation in order to communicate with the K8S cluster.

For example, if the installation executes from the local directory `~/sibel-install`, then the `kubeconfig` will be stored as `~/sibel-install/kubeconfig` on the local machine.

To communicate with the K8S API `kubectl` is required. It can be downloaded from https://kubernetes.io/docs/tasks/tools/

To simplify the communication with the K8S cluster the the file `~/sibel-install/kubeconfig` could be copied to `~/.kube` directory with the name `config` which is a location `kubectl` checks and use by default.
```shell
mkdir -p ~/.kube
cp ~/sibel-install/kubeconfig ~/.kube/config
```

The following command could be executed to validate if all is done correctly and the connection to K8S API works:

```shell
kubectl get no

# the output should be similar to the below
NAME       STATUS   ROLES                       AGE   VERSION
master-1   Ready    control-plane,etcd,master   23d   v1.29.0+rke2r1
worker-1   Ready    <none>                      23d   v1.29.0+rke2r1
worker-2   Ready    <none>                      23d   v1.29.0+rke2r1
worker-3   Ready    <none>                      23d   v1.29.0+rke2r1
```


If you see the error like `The connection to the server localhost:8080 was refused - did you specify the right host or port?` that means that the `config` file is missing in the default `~/.kube` location. Make sure that the file is copied from the installation location to the default one and try again. The file should be exactly `config`  and be located in  `~/.kube` directory.

The file `~/.kube/config` should look similar to below:
```shell
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: <REDACTED>
    server: https://<K8S-API-ADDRESS>:6443
  name: default
contexts:
- context:
    cluster: default
    namespace: central-hub
    user: default
  name: dev@cluster.local
current-context: dev@cluster.local
kind: Config
preferences: {}
users:
- name: default
  user:
    client-certificate-data: <REDACTED>
    client-key-data: <REDACTED>
```


### Central Hub deployment failures during the installation process

#### DNS resolution errors during the installation

During the installation process you may encounter the following error or something similar to it:
```shell
k8s-api.control-lb.qa.tucana.sibel.health on 192.168.65.7:53: no such host
```
In most of the cases it means that the step to create DNS records from the installation manual has been skipped. The DNS records are required for the Central Hub components to communicate with each other. The DNS records should be created in the DNS provider for the domain that is used for the Central Hub deployment and also for K8S API domain.

The DNS records should be created for the following domains:
  * domain name for the Kubernetes API, should be pointing to the IP address of the load balancer that was created during the VMs setup.
  E.g. `k8s-api.hq.tucana.sibel.health` > `192.168.1.81` (IP of the VM with HAproxy loadbalancer for K8S API)
  * domain name for the Central Hub API, should be pointing to the IP address of the load balancer that was created during the VMs setup.
  E.g. `api.hq.tucana.sibel.health` > `192.168.1.81` (IP of the VM with HAproxy loadbalancer for Central Hub API)
  * domain name for the Central Hub CMS, should be pointing to the IP address of the load balancer that was created during the VMs setup.
  E.g. `cms.hq.tucana.sibel.health` > `192.168.1.81` (IP of the VM with HAproxy loadbalancer for Central Hub API)

As a workaround for K8S API domain, you can add the following line to the `/etc/hosts` file on the machine where the installation is executed:
```shell
k8s-api.control-lb.qa.tucana.sibel.health <IP of the VM with HAproxy loadbalancer for K8S API>
```


### How to access K8 dashboard

The Kubernetes dashboard is available via the link https://dash.${your-domain-name}
To be able to access the dashboard you need to make sure that the DNS record exists for this domain in you DNS provider.

Authentication to the dashboard can be done using the `kubeconfig` file generated during the installation OR using a token.

* Please see "General info about Central Hub deployment" on how to get the `kubeconfig` file.
* The token can be retrieved from the K8S cluster using `kubectl` tool as following:
```shell
kubectl get secret -n dashboard dashboard-central-hub-admin-token -ojsonpath={.data.token} | base64 -d
```

### Central Hub is mulfunctioning

If the Central Hub is not functioning as expected, the following steps can be taken to troubleshoot the issue:

1. Check the status of the Central Hub components using the following command:
```shell
kubectl get po -n central-hub

NAME                                             READY   STATUS      RESTARTS         AGE
audit-trail-75c6974c54-bcc86                     1/1     Running     0                5d20h
authentication-646d5bb5b8-66jgt                  1/1     Running     0                5d20h
authentication-646d5bb5b8-xrwss                  1/1     Running     0                5d20h
central-monitoring-7fb97bc69c-8k84r              1/1     Running     0                5d20h
device-64b948f8f8-clzwd                          1/1     Running     0                5d20h
device-64b948f8f8-zkrb9                          1/1     Running     0                5d20h
kafka-cluster-entity-operator-8469564b7b-ntjz6   3/3     Running     0                6d21h
kafka-cluster-kafka-0                            1/1     Running     0                6d21h
kafka-cluster-kafka-1                            1/1     Running     0                6d21h
kafka-cluster-kafka-2                            1/1     Running     0                6d21h
kafka-cluster-zookeeper-0                        1/1     Running     0                6d21h
kafka-cluster-zookeeper-1                        1/1     Running     0                6d21h
kafka-cluster-zookeeper-2                        1/1     Running     0                6d21h
kafka-s3-sink-connect-5867bc8c5d-7jd47           1/1     Running     0                6d21h
mirth-6cd774f455-d8x9n                           1/1     Running     0                5d20h
patient-5454898fc4-4pktk                         1/1     Running     0                5d20h
patient-5454898fc4-lxkf9                         1/1     Running     0                5d20h
postgres-1-0                                     1/1     Running     0                23d
realtime-f9b4dc4d6-rmh6x                         1/1     Running     0                5d20h
redis-0                                          1/1     Running     0                12d
rkc-75764fd49c-9zgqr                             1/1     Running     0                5d20h
sdc-follower-7b8fb6b49b-26wjw                    1/1     Running     0                6d21h
sdc-follower-7b8fb6b49b-fmfq6                    1/1     Running     0                6d21h
sdc-follower-7b8fb6b49b-ljpc9                    1/1     Running     0                6d21h
sdc-leader-5568568cd4-k4lzn                      1/1     Running     0                5d20h
web-86c585ffc5-2q4nz                             1/1     Running     0                5d20h
web-86c585ffc5-pm4zm                             1/1     Running     0                5d20h


```
Alternatively, you can do the same using the K8S dashboard. Login to the dashboard and navigate to the `central-hub` namespace and check the status of the pods on the `Workloads` page.

2. If there are pods that are not `Running` or `Completed`, check the logs of the pod to identify the issue. The logs can be checked using the following command:
```shell
kubectl logs -n central-hub <pod-name>
```

Or, using the K8S dashboard. Navigate to the `central-hub` namespace and check the logs of the pod on the `Workloads` page.

3. If some of the pods are in `Pending` state, check the events of the pod to identify the issue. The events can be checked using the following command:
```shell
kubectl describe po -n central-hub <pod-name>
```

Or, using the K8S dashboard. Navigate to the `central-hub` namespace and check the events of the pod on the `Workloads` page.

Events are usually self-explanatory and can help to identify the issue.

As a possible reason for the pending pods could be that the node where the pod should be scheduled is not ready or there are not enough resources on the node to schedule the pod.

The node status can be checked using the following command:
```shell
kubectl get no

NAME       STATUS   ROLES                       AGE   VERSION
master-1   Ready    control-plane,etcd,master   28d   v1.29.0+rke2r1
worker-1   Ready    <none>                      28d   v1.29.0+rke2r1
worker-2   Ready    <none>                      28d   v1.29.0+rke2r1
worker-3   Ready    <none>                      28d   v1.29.0+rke2r1
```

If one of the nodes is not `Ready`, check the events and state of the node to identify the issue using the following command:
```shell
kubectl describe no <node-name>
```

Read the output carefully to identify issues with the node if any.


### Central Hub URL is not accessible

If the Central Hub URL is not accessible, the following steps can be taken to troubleshoot the issue:

1. Make sure the the DNS record exists for the Central Hub URL in your DNS provider. The correct IP address is the IP address of the load balancer that was created during the installation process. 

2. If the DNS record exists, check the status of the load balancer on the corresponding VM using the following command:
```shell
sudo docker compose -f haproxy/docker-compose.yaml ps

NAME      IMAGE         COMMAND                  SERVICE   CREATED       STATUS       PORTS
haproxy   haproxy:2.7   "docker-entrypoint.s…"   haproxy   3 weeks ago   Up 3 weeks   0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:443->443/tcp, :::443->443/tcp, 0.0.0.0:6443->6443/tcp, :::6443->6443/tcp, 0.0.0.0:6661->6661/tcp, :::6661->6661/tcp, 0.0.0.0:8080->8080/tcp, :::8080->8080/tcp, 0.0.0.0:8443->8443/tcp, :::8443->8443/tcp
```

If the state of the `haproxy` service is not `Up`, check the logs of the service to identify the issue using the following command:
```shell
sudo docker compose -f haproxy/docker-compose.yaml logs haproxy
```
3. If the state of the `haproxy` service is `Up`, than the next step would be to check if the ingress controller in the K8S cluster is working correctly. The ingress controller is responsible for routing the traffic to the correct service in the K8S cluster.
To check the status of the ingress controller, use the following command:
```shell
kubectl get po -n ingress-nginx

NAME                             READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-4c7lm   1/1     Running   0          18d
ingress-nginx-controller-qlph6   1/1     Running   0          11d
ingress-nginx-controller-zf8xn   1/1     Running   0          11d
```

If all pods are in `Running` state, check the logs of the ingress controller to identify the issue using the following command:
```shell
kubectl logs -l app.kubernetes.io/instance=ingress-nginx -n ingress-nginx -f
```
The command above will follow the logs of ingress-controller pods and will show the logs in real-time. Try to connect to the URL and check the logs for any errors.

You can use `grep` during the logs check to investigate the specific hostname that is not accessible to identify the problem. If the logs for the hostname are present in the logs, the problem is most likely with the Central Hub components receiving the traffic.

4. Check the logs of the faulty Central Hub components to identify the issue using the following command:
```shell
kubectl logs -n central-hub <pod-name>
```

### Patient Monitor is not able to connect to the Central Hub
1. Make sure that Patient Monitor is running is SDC mode.

2. Make sure that Patient Monitor and Central Hub are in the same broadcast network domain.

3. Check the logs of SDC leader and SDC followers pods in the cluster to identify a possible cause of the issue.
```shell
kubectl logs -l app.kubernetes.io/instance=sdc -n central-hub -f
```

The command above will follow the logs of the SDC pods and will show the logs in real-time. Try to connect the Patient Monitor to the Central Hub and check the logs for any errors.

### Connection issues between the pods in the cluster while pods are running on the different nodes
1. Kubernetes cluster uses the overlay network to connect the pods running on different nodes. The overlay network is created by the CNI plugin that is installed on the cluster. The CNI plugin is responsible for creating the network and managing the network traffic between the pods.

2. If the pods are not able to communicate with each other, check the status of the nodes first using the following command:
```shell
kubectl get no

# the output should be similar to the below
NAME       STATUS   ROLES                       AGE   VERSION
master-1   Ready    control-plane,etcd,master   23d   v1.29.0+rke2r1
worker-1   Ready    <none>                      23d   v1.29.0+rke2r1
worker-2   Ready    <none>                      23d   v1.29.0+rke2r1
worker-3   Ready    <none>                      23d   v1.29.0+rke2r1
```

3. If the nodes are `Ready`, check the status of the CNI pods using the following command:
```shell
kubectl get po -n kube-system -l app.kubernetes.io/part-of=cilium -owide
# the output should be similar to the below
NAME                               READY   STATUS    RESTARTS   AGE   IP              NODE       NOMINATED NODE   READINESS GATES
cilium-operator-57569989c9-rwn8w   1/1     Running   0          31d   192.168.0.141   master-1   <none>           <none>
cilium-operator-57569989c9-sf72k   1/1     Running   0          31d   192.168.0.89    worker-2   <none>           <none>
cilium-z8h7b                       1/1     Running   0          31d   192.168.0.141   master-1   <none>           <none>
cilium-rzplx                       1/1     Running   0          31d   192.168.0.89    worker-2   <none>           <none>
cilium-96qkl                       1/1     Running   0          31d   192.168.1.249   worker-3   <none>           <none>
cilium-sccgp                       1/1     Running   0          31d   192.168.1.214   worker-1   <none>           <none>
```

If the pods are not in `Running` state, check the logs of the pod to identify the issue using the following command:
```shell
kubectl logs -n kube-system <pod-name>
```


### Cluster IP addresses change after the reboot of the server
> **WARNING**:
> Precautions should be taken to avoid the change of the IP addresses of the nodes in the Kubernetes cluster after the reboot of the server. 
> Make sure that the IPs assigned to the Kubernetes cluster nodes are static and are not assigned by the DHCP server in the network.

In case the IP addresses of the nodes in the Kubernetes cluster change after the reboot of the server, the Kubernetes cluster should be reset with the new IPs. The following steps should be taken to reset the Kubernetes cluster with the new IPs:

1. Connect to the control plane node of the Kubernetes cluster using SSH.
2. Open the file `/etc/rancher/rke2/config.yaml` and comment out `server` configuration key

```
vi /etc/rancher/rke2/config.yaml

# server: https://<OLD_IP_ADDRESS>:9345
token: <REDACTED>
data-dir: /var/lib/rancher/rke2
cni: ['cilium']
tls-san:
  - <OMMITED>
node-taint:
  - CriticalAddonsOnly=true:NoExecute
disable: ['rke2-ingress-nginx', 'rke2-canal']
```

3. Stop rke2-server service
```shell
service rke2-server stop
```

4. Reset the cluster
```shell
rke2 server --cluster-reset
```

5. Check the status of the rke2-server service
```shell
service rke2-server status
```

5. Check the cluster nodes status
```shell
kubectl get no -owide

# the output could be similar to the below
NAME       STATUS   ROLES                       AGE   VERSION          INTERNAL-IP        EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
master-1   Ready    control-plane,etcd,master   48d   v1.29.0+rke2r1   <NEW_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
worker-1   NotReady <none>                      48d   v1.29.0+rke2r1   <OLD_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
worker-2   NotReady <none>                      48d   v1.29.0+rke2r1   <OLD_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
worker-3   NotReady <none>                      48d   v1.29.0+rke2r1   <OLD_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
```

Worker nodes are not ready because the IPs are changed. The next step is to update the IPs of the worker nodes in the cluster.

1. Delete the worker nodes from the cluster
```shell
kubectl delete no worker-1 worker-2 worker-3
```

2. Connect to each worker node via SSH and update the IP address in the `/etc/rancher/rke2/config.yaml` file.
It should be the IP address of the control plane node, NOT THE NODE IP ADDRESS.
The cluster worker node will connect to the control plane node to register itself.

```shell
vi /etc/rancher/rke2/config.yaml

server: https://<NEW_IP_ADDRESS_OF_THE_MASTER_NODE>:9345
token: <REDACTED>
data-dir: /var/lib/rancher/rke2
cni: ['cilium']
tls-san:
  - <OMMITED>
node-taint:
  - CriticalAddonsOnly=true:NoExecute
disable: ['rke2-ingress-nginx', 'rke2-canal']
```

3. Stop the rke2-agent service on the worker node
```shell
service rke2-agent stop
```

4. Start the rke2-agent service on the worker node
```shell
service rke2-agent start
```

5. Check the status of the rke2-agent service
```shell
service rke2-agent status
```

6. Check the status of the worker node in the cluster
```shell
kubectl get no -owide 

# the output could be similar to the below
NAME       STATUS   ROLES                       AGE   VERSION          INTERNAL-IP        EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION       CONTAINER-RUNTIME
master-1   Ready    control-plane,etcd,master   48d   v1.29.0+rke2r1   <NEW_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
worker-1   Ready <none>                         48d   v1.29.0+rke2r1   <NEW_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
worker-2   Ready <none>                         48d   v1.29.0+rke2r1   <NEW_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
worker-3   Ready <none>                         48d   v1.29.0+rke2r1   <NEW_IP_ADDRESS>   <none>        Ubuntu 22.04.3 LTS   5.15.0-106-generic   containerd://1.7.11-k3s2
```


### PostgreSQL database backup

***The configuration here is based on the assumption that the backup is stored in the S3 bucket. Adjust the script accordingly to leverage other storage solutions.***

In order to enable the backup of the PostgreSQL database, the following steps should be taken:

1. Adjust `base-kubegres-config` ConfigMap in `central-hub` namespace to include the following `backup_database.sh` key with the script that will be executed to backup the database. The script should be able to connect to the database and create a dump of the database. The script should also be able to upload the dump to the S3 bucket. 

```shell
  # Some env like $KUBEGRES_RESOURCE_NAME, $BACKUP_SOURCE_DB_HOST_NAME are defined by the container.
  backup_database.sh: |
    #!/bin/bash
    set -e

    apt-get update -y && apt-get install -y awscli

    dt=$(date '+%d/%m/%Y %H:%M:%S');
    fileDt=$(date '+%d_%m_%Y_%H_%M_%S');
    backUpFileName="$KUBEGRES_RESOURCE_NAME-backup-$fileDt.gz"
    backUpFilePath="/var/lib/backup/$backUpFileName"

    echo "$dt - Starting DB backup of Kubegres resource $KUBEGRES_RESOURCE_NAME into file: $backUpFilePath";
    echo "$dt - Running: pg_dumpall -h $BACKUP_SOURCE_DB_HOST_NAME -U postgres -c | gzip > $backUpFilePath"

    pg_dumpall -h $BACKUP_SOURCE_DB_HOST_NAME -U postgres -c | gzip > $backUpFilePath

    if [ $? -ne 0 ]; then
      rm $backUpFilePath
      echo "Unable to execute a backup. Please check DB connection settings"
      exit 1
    fi

    echo "$dt - DB backup completed for Kubegres resource $Kubegres_RESOURCE_NAME into file: $backUpFilePath";

    echo "Uploading the dump to S3";

    aws s3 cp "$backUpFilePath" "s3://$AWS_S3_BUCKET/$AWS_S3_BACKUP_DIR";

    echo "$dt - DB backup uploaded to s3://$AWS_S3_BUCKET/$AWS_S3_BACKUP_DIR";

```

2. Create a secret in the `central-hub` namespace with the AWS credentials that will be used to upload the backup to the S3 bucket. The secret should contain the following:
```shell
apiVersion: v1
kind: Secret
metadata:
  name: aws-s3-backup-creds
  namespace: central-hub
type: Opaque
stringData:
  AWS_ACCESS_KEY_ID: <AWS_ACCESS_KEY_ID>
  AWS_SECRET_ACCESS_KEY: <AWS_SECRET_ACCESS_KEY>
  AWS_S3_BUCKET: <AWS_S3_BUCKET>
```


3. Adjust `kind: Kubegres` resource in `central-hub` namespace to include the following environment variables:
***DO NOT REMOVE EXISTING SPECIFICATION, JUST ADD THE FOLLOWING LINES TO THE END OF THE ENVIRONMENT SECTION***
```shell
  env:
      - name: AWS_ACCESS_KEY_ID
        valueFrom:
           secretKeyRef:
              name: aws-s3-backup-creds
              key: AWS_ACCESS_KEY_ID
      - name: AWS_SECRET_ACCESS_KEY
        valueFrom:
           secretKeyRef:
              name: aws-s3-backup-creds
              key: AWS_SECRET_ACCESS_KEY
      - name: AWS_S3_BUCKET
        valueFrom:
           secretKeyRef:
              name: aws-s3-backup-creds
              key: AWS_S3_BUCKET
      - name: AWS_S3_BACKUP_DIR
        value: <path/in/s3-bucket>
```

and 

***DO NOT REMOVE EXISTING SPECIFICATION, JUST ADD THE FOLLOWING LINES WITH PROPER INDENTATION TO THE SPEC SECTION***
```shell
spec:
   backup:
     schedule: "00 1 * * *"
     pvcName: postgres-db-backup
     volumeMount: /var/lib/backup
```

### PostgreSQL database restore

Taking into account that the database instance is running in the Kubernetes cluster the person who will do the restore should have an access to the Kubernetes API via kubectl tool or via any form of pre-configure GUI (K8S Dashboard, etc) with the permissions to create pod.

1. Spin up a pod with all necessary tools for the restore or with an ability to download the required tools and with the access to the running pod with PostgreSQL databases.

2. The step by step procedure for restore the whole cluster including all databases:

```shell
# Run the pod with pgsql tools
kubectl run pgsql-shell --rm -i --tty --image postgres:14.1 -n tucana -- /bin/bash

# Set the required variables
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="<pg_password>"
export POSTGRES_HOST="postgres.central-hub.svc.cluster.local"
export AWS_S3_BUCKET="<aws_s3_bucket>"
export AWS_S3_BACKUP_DIR="<aws_s3_backup_dir>"
export AWS_S3_BACKUP_DUMP="<aws_s3_backup_dump_file_name>"
export AWS_ACCESS_KEY_ID="<aws_access_key>"
export AWS_SECRET_ACCESS_KEY="<aws_secret_access_key>"

# Install aws cli tool
apt-get update -y && apt-get install -y awscli

# Download the backup from S3 and gunzip it
aws s3 cp s3://${AWS_S3_BUCKET}/${AWS_S3_BACKUP_DIR}/${AWS_S3_BACKUP_DUMP} ./
gunzip -c ${AWS_S3_BACKUP_DUMP} > dumpall.sql 

# Restore the whole cluster from the dump
psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST} < dumpall.sql

# Connect to the instance to validate the data
psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}
```

3. The step by step procedure for restore a particular database (will partly repeat the steps from above):

```shell
# Run the pod with pgsql tools
kubectl run pgsql-shell --rm -i --tty --image postgres:14.1 -n tucana -- /bin/bash

# Set the required variables
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="<pg_password>"
export POSTGRES_HOST="postgres.central-hub.svc.cluster.local"
export AWS_S3_BUCKET="<aws_s3_bucket>"
export AWS_S3_BACKUP_DIR="<aws_s3_backup_dir>"
export AWS_S3_BACKUP_DUMP="<aws_s3_backup_dump_file_name>"
export AWS_ACCESS_KEY_ID="<aws_access_key>"
export AWS_SECRET_ACCESS_KEY="<aws_secret_access_key>"

# Install aws cli tool
apt-get update -y && apt-get install -y awscli

# Download the backup from S3 and gunzip it
aws s3 cp s3://${AWS_S3_BUCKET}/${AWS_S3_BACKUP_DIR}/${AWS_S3_BACKUP_DUMP} ./
gunzip -c ${AWS_S3_BACKUP_DUMP} > dumpall.sql 

# Define a variable for the target database
export POSTGRES_DB_TO_RESTORE="patient"

# Extract the required piece of dump from dumpall.sql
sed  "/connect.*${POSTGRES_DB_TO_RESTORE}/,\$!d" dumpall.sql | sed "/PostgreSQL database dump complete/,\$d" > ${POSTGRES_DB_TO_RESTORE}.dump

# (Optional) Drop the target database if it exists by this point
echo "DROP DATABASE ${POSTGRES_DB_TO_RESTORE}" | psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/postgres

# Create the target database
echo "CREATE DATABASE ${POSTGRES_DB_TO_RESTORE}" | psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/postgres

# Restore the database
psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST} ${POSTGRES_DB_TO_RESTORE} < ${POSTGRES_DB_TO_RESTORE}.dump

# Connect to the instance to validate the data
psql postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}
```
