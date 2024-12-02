# SDC 11073 Gateway

SDC 11073 Gateway is a service designed to connect to 11073 compatible devices available in the same network. It relies on the implementation of the 11073 standard found in the SDC-RI (SDC Reference Implementation) project. This repository adds some more features for scalability improvements to the Consumer 1 implementation found in SDC-RI.

## How it works

## Background

The SDC-RI project relies on the following libraries:

DWPS: Device discovery over the network
Biceps: Communication protocol with devices
Glue: Gets DWPS and Biceps together
This service showcases how to use these libraries in order to discover devices and subscribe to its services.

## Current implementation

The service has a device discovery service (thread) that runs non-stop while the SDC service is running. It scans the network every 30 seconds or so to find new devices. Devices will also broadcast their existence when connecting to the network for the first time, but for reliability in case the broadcast message is missed, there is the scan.

Once the scan is done, it sends discovered devices to a processing queue. This queue is consumed by a set of threads that check if no one is actually monitoring the device. If the device is not being monitored, it starts device monitoring. If it is being monitored, it ignores the device.

As part of device monitoring, the service subscribes to events incoming from the device (using 11073). Once the subscription is done, the service receives HTTP calls every time there is a new event. The report processor contains the definitions of how to handle incoming messages. Currently, the service is only handling the subscription to new waveform data. Every time new waveform data is posted, it is sent to Kafka so that other services can consume it.

## Pending work

The following are some pending improvements for the service:

- Add multi-thread support when consuming from the device discovered queue (currently using only one thread)

## Run multiple instances using docker 

You need to add the following to the `docker-compose.yml` file

```yaml
  sdc:
    image: sibel/sdc
    build:
      dockerfile: gateways/sdc/Dockerfile
    network_mode: "host"
    deploy:
      mode: replicated
      replicas: 4
    volumes:
      - "./gateways/sdc/src/main/resources/crypto:/opt/resources"
    environment:
      HOST_IP_ADDR: "192.168.1.8"
      REDIS_HOST: "localhost"
      REDIS_PORT: "6379"
      KAFKA_HOST: "localhost"
      KAKFA_PORT: "9092"
      KAFKA_TOPIC_VITALS: "vitals"
      PROBE_INTERVAL: "10"
      CLAIM_INTERVAL: "3"
      KAFKA_TOPIC_DEVICE: "events-sdc"
      KAFKA_TOPIC_DEVICE_COMMANDS: "device-commands-requests"
      KAFKA_TOPIC_DEVICE_COMMANDS_RESPONSE: "device-commands-responses"
      KAFKA_TOPIC_ALERT: "alerts"
      KAFKA_TOPIC_TECHNICAL_ALERT: "technical-alerts"
      KAFKA_TOPIC_SDC_REALTIME_STATE: "sdc-realtime-state"
      KAFKA_TOPIC_PATIENT_EVENTS: "events-patient"
      CRYPTO_USER_KEY_PATH: "/opt/resources/consumerLeaf1.key"
      CRYPTO_USER_CERT_PATH: "/opt/resources/consumerLeaf1.crt"
      CRYPTO_CA_CERT_PATH: "/opt/resources/intermediateCA.crt"
      FOLLOWER_MAX_CONNECTED_DEVICES: "2"
```

## Emulator

By default `mvn clean package` generates the `Consumer` class which is the one that will run on the server and receive the connection of the PMs. But it can be specified to build another class which is the `Provider`, which emulates the behavior of a PM. To package the `Provider` instead of the `Consumer` you must run:

```shell
mvn -DtargetClass=Provider clean package
```

This command will generate instead of the `Consumer-${version}.jar` will generate the `Provider-${version}.jar` which will run the PM emulation when started.
You need to add the following to the `docker-compose.yml` file
