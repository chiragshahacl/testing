#!/bin/bash

# login into docker dev repository
# you need to have a valid AWS session initiated
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 643361541825.dkr.ecr.us-east-2.amazonaws.com


