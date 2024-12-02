#!/bin/bash

# login into docker dev repository
# you need to have a valid AWS session initiated
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 104472814609.dkr.ecr.us-east-2.amazonaws.com


