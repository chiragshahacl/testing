# RKC

# 📔 Documentation
This app is designed to handle Kafka messages and process them in a concurrent way.
It utilizes [Flume](https://docs.rs/flume/latest/flume/) as a Multi-Producer Multi-Consumer (MPMC) channel to manage concurrent message processing.
The application is structured into different modules:

* Consumer: Responsible for consuming Kafka messages.
* Processor: Contains various processors for handling Kafka messages, must implement the `Processor` trait.
* Utils: Provides utility functions and structs for the application, such as parsing each message.

## 💻 Running locally
Make sure you have rustup installed and cmake

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

For Mac
```bash
brew install cmake
```

Run unoptimized dev version
```sh
cargo run
```

Run optimized version
```sh
cargo run --release
```

Create build and run binary
```sh
cargo build --release
./target/release/rkc
```

## 🧪 Test integration with Kafka
To try this project, you can use `kafka-producer-perf-test`.
You can find a sample payloads in `benchmark/`

For example:

```bash
kafka-producer-perf-test --topic vitals --throughput -1 --num-records 1000 --producer-props bootstrap.servers=broker:29092 --payload-file benchmark/payload.json
```
