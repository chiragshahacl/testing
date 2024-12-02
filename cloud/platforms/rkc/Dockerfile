# Create a builder image
FROM clux/muslrust:stable as builder

WORKDIR /home/app

COPY platforms/rkc platforms/rkc
WORKDIR /home/app/platforms/rkc
RUN cargo build --release
RUN cp target/*/release/rkc .

# Create a minimal docker image
FROM scratch
COPY --from=builder /home/app/platforms/rkc/rkc /home/app/platforms/rkc/*.env /

ARG SIBEL_VERSION="undefined"
ENV SIBEL_VERSION=${SIBEL_VERSION}

CMD ["/rkc"]
