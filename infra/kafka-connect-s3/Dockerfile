FROM confluentinc/cp-kafka-connect:7.4.2 as confluent

ENV KAFKA_CONNECT_S3_VERSION="10.5.6"

RUN confluent-hub install confluentinc/kafka-connect-s3:${KAFKA_CONNECT_S3_VERSION}  --no-prompt

FROM quay.io/strimzi/kafka:0.33.2-kafka-3.4.0
USER root:root

COPY --from=confluent /usr/share/confluent-hub-components/confluentinc-kafka-connect-s3 /opt/kafka/plugins/confluentinc-kafka-connect-s3

USER 1001