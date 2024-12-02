use flume::{Receiver, Sender};
use rdkafka::message::OwnedMessage;
use tokio::task::JoinHandle;
use tokio_util::sync::CancellationToken;
use tracing::Instrument;

use crate::{
    consumer::kafka_consumer,
    utils::{AppConfig, Commit, HealthState},
};

pub fn spawn_consumer(
    config: &AppConfig,
    tx: Sender<OwnedMessage>,
    commit_channel: Receiver<Commit>,
    cancellation_token: &CancellationToken,
    heartbeat_tx: Sender<HealthState>,
) -> JoinHandle<()> {
    tokio::spawn(
        kafka_consumer(
            config.clone(),
            tx.clone(),
            commit_channel,
            cancellation_token.clone(),
            heartbeat_tx,
        )
        .instrument(tracing::info_span!("[Kafka Consumer ♻️]")),
    )
}
