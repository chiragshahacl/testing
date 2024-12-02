FROM nextgenhealthcare/connect:4.5.0

RUN curl -L -O https://github.com/SagaHealthcareIT/mirthsync/releases/download/3.1.0/mirthsync-3.1.0.zip \
    && unzip mirthsync-3.1.0.zip -d .

EXPOSE 8443/tcp

ENV CONFIG_PATH="tucana_config" \
    MIRTHSYNC_PATH="./mirthsync-3.1.0/bin/" \
    _MP_SERVER_API_ACCESSCONTROLALLOWORIGIN="*"

COPY gateways/mirth/mirth.properties ./conf/mirth.properties
COPY gateways/mirth/tucana_config $CONFIG_PATH
COPY gateways/mirth/sync.sh .

USER $USERNAME
ENV VMOPTIONS -Xmx2G

CMD ["./mcserver"]
