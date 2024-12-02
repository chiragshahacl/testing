use crate::utils::{AppConfig, HealthState};
use crate::Commit;
use flume::{Receiver, Sender};
use futures::stream::StreamExt;
use rdkafka::config::RDKafkaLogLevel;
use rdkafka::{
    consumer::{Consumer, StreamConsumer},
    message::OwnedMessage,
    ClientConfig,
};
use std::str;
use tokio_util::sync::CancellationToken;
use tracing::{error, info, warn};

fn create_consumer(config: AppConfig) -> StreamConsumer {
    let consumer_result: Result<StreamConsumer, rdkafka::error::KafkaError> =
        match config.environment.as_str() {
            "local" => ClientConfig::new()
                .set("bootstrap.servers", config.kafka_server)
                .set("group.id", config.kafka_group)
                .create(),
            _ => ClientConfig::new()
                .set("bootstrap.servers", config.kafka_server)
                .set("group.id", config.kafka_group)
                .set("security.protocol", "SSL")
                .set("ssl.keystore.password", config.kafka_password)
                .set("ssl.ca.location", config.kafka_ca_file_path)
                .set("ssl.key.location", config.kafka_key_file_path)
                .set("ssl.certificate.location", config.kafka_cert_file_path)
                .set("enable.ssl.certificate.verification", "true")
                .set("enable.auto.commit", "true")
                .set("auto.commit.interval.ms", "15000") // Commit automatically every 15 seconds.
                .set("enable.auto.offset.store", "false") // but only commit the offsets explicitly stored via `consumer.store_offset`.
                .set_log_level(RDKafkaLogLevel::Debug)
                .create(),
        };

    let consumer = consumer_result.expect("Couldn't create consumer");

    info!("🤝 Connection success on {}", config.environment);

    consumer
}

pub async fn message_receive_process(
    consumer: &StreamConsumer,
    tx: Sender<OwnedMessage>,
    heartbeat_tx: Sender<HealthState>,
) {
    while let Some(result) = consumer.stream().next().await {
        match result {
            Ok(message) => {
                match tx.send(message.detach()) {
                    Ok(_) => {}
                    Err(e) => error!("Sending message to main thread failed: {:?}", e),
                };
            }
            Err(e) => {
                error!("Error message received: {:?}", e);
                let _ = heartbeat_tx.send(HealthState::Unhealthy(format!(
                    "Kafka connection issues {e}"
                )));
            }
        }
    }
}

pub async fn commit_messages(consumer: &StreamConsumer, commit_channel: Receiver<Commit>) {
    while let Ok(commit) = commit_channel.recv_async().await {
        match consumer.store_offset(commit.topic.as_str(), commit.partition, commit.offset) {
            Ok(_) => {}
            Err(e) => error!("Failed to store offset {}: {}", commit.offset, e),
        }
    }
}

pub async fn kafka_consumer(
    config: AppConfig,
    tx: Sender<OwnedMessage>,
    commit_channel: Receiver<Commit>,
    cancellation_token: CancellationToken,
    heartbeat_tx: Sender<HealthState>,
) {
    info!("Starting to consume");
    info!(
        "🛜 Connecting to {}, Group: {}",
        config.kafka_server, config.kafka_group
    );

    let topics: &[&str] = &config
        .kafka_topics
        .iter()
        .map(|s| s.as_str())
        .collect::<Vec<&str>>();

    info!("📩 Subscribing to {:?} topics", topics);

    let consumer = &create_consumer(config.clone());

    consumer
        .subscribe(topics)
        .expect("subscribing to {topics} failed");

    info!("✅ Subscription success");

    tokio::select! {
       _ = cancellation_token.cancelled() => {
           warn!("🔌 Shutdown signal received, gracefully shutting down...");

           if !commit_channel.is_empty() {
               warn!("Commiting pending messages");
               while !commit_channel.is_empty() {
                   if let Ok(commit) = commit_channel.recv_async().await {
                       match consumer.store_offset(commit.topic.as_str(), commit.partition, commit.offset) {
                           Ok(_) => {},
                           Err(e) => error!("Failed to store offset {}: {}", commit.offset, e),
                       }
                   }
               }
           }

       },
       _ = message_receive_process(consumer, tx, heartbeat_tx) => {}
       _ = commit_messages(consumer, commit_channel.clone()) => {}
    }
    warn!("Shutdown");
}
