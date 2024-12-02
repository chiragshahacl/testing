# CMS Installer CLIP App

# Development 

## Installation

Run `poetry install`

## Execution

Run `./run.sh`


## Compilation

Run `./compile.sh`


# How to pull the installer image locally

* [Setup AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#cli-configure-sso-configure) for prod env, make sure to name the profile `tucana-prod` 

* Enable profile for current shell

```shell
export AWS_PROFILE=tucana-prod
```

* Login using sso

```shell
aws sso login --profile tucana-prod
```

* Login to docker

```shell
aws ecr get-login-password | docker login --username AWS --password-stdin 620908046246.dkr.ecr.us-east-2.amazonaws.com
```

* Pull the installer image

```shell
docker pull 620908046246.dkr.ecr.us-east-2.amazonaws.com/install:{desired_tag}
```

* Convert to tar

```shell
docker save 620908046246.dkr.ecr.us-east-2.amazonaws.com/install > install.tar
```

