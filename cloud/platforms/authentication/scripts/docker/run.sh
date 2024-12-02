docker run --env-file=.env -e ENVIRONMENT=docker --name=authentication -d -p 7000:7000 --network tucana authentication:local
