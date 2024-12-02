# Use imutable image tags rather than mutable tags (like ubuntu:22.04)
FROM ubuntu:jammy-20230308
# Some tools like yamllint need this
# Pip needs this as well at the moment to install ansible
# (and potentially other packages)
# See: https://github.com/pypa/pip/issues/10219
ENV LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1

ARG HELM_VERSION=3.12.2
ARG CRANE_VERSION=v0.17.0
ARG YQ_VERSION=v4.40.5

ARG SCI_CHART_SERVER_KEY
ENV SCI_CHART_SERVER_KEY=$SCI_CHART_SERVER_KEY

ARG CENTRAL_HUB_RELEASE_TAG
ENV CENTRAL_HUB_RELEASE_TAG=$CENTRAL_HUB_RELEASE_TAG

RUN apt update -q \
    && apt install -yq --no-install-recommends \
       curl \
       python3 \
       python3-pip \
       sshpass \
       vim \
       rsync \
       openssh-client \
       unzip \
       gettext-base \
       jq \
       whois \
    && pip install --no-compile --no-cache-dir \
       ansible==7.6.0 \
       ansible-core==2.14.6 \
       cryptography==41.0.1 \
       jinja2==3.1.2 \
       netaddr==0.8.0 \
       jmespath==1.0.1 \
       MarkupSafe==2.1.3 \
       ruamel.yaml==0.17.21 \
       passlib==1.7.4 \
    && rm -rf /var/lib/apt/lists/* /var/log/* \
    && find /usr -type d -name '*__pycache__' -prune -exec rm -rf {} \;

# Copy installation files
COPY ./installation-pack /install

# Install Kubectl
RUN KUBE_VERSION=$(sed -n 's/^rke2_version: \(.*\)+.*/\1/p' /install/rke2/defaults/main.yml) \
    && curl -L https://dl.k8s.io/release/$KUBE_VERSION/bin/linux/$(dpkg --print-architecture)/kubectl -o /usr/local/bin/kubectl \
    && echo $(curl -L https://dl.k8s.io/release/$KUBE_VERSION/bin/linux/$(dpkg --print-architecture)/kubectl.sha256) /usr/local/bin/kubectl | sha256sum --check \
    && chmod a+x /usr/local/bin/kubectl

# Install Helm
RUN curl https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz -o helm.tar.gz \
    && tar -xzf helm.tar.gz \
    && mv linux-amd64/helm /usr/local/bin/helm \
    && chmod +x /usr/local/bin/helm \
    && rm -rf helm.tar.gz linux-amd64

# Install yq
RUN curl -L https://github.com/mikefarah/yq/releases/download/${YQ_VERSION}/yq_linux_amd64.tar.gz -o yq.tar.gz \
    && tar -xzf yq.tar.gz \
    && mv yq_linux_amd64 /usr/local/bin/yq \
    && rm -rf yq* install-man-page.sh

# Install aws cli
RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Install Crane
RUN curl -sL "https://github.com/google/go-containerregistry/releases/download/${CRANE_VERSION}/go-containerregistry_Linux_x86_64.tar.gz" > go-containerregistry.tar.gz \
    && tar -zxvf go-containerregistry.tar.gz -C /usr/local/bin/ crane \
    && rm -rf go-containerregistry.tar.gz

# Install Taskfile
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

WORKDIR /install
CMD ["bash"]