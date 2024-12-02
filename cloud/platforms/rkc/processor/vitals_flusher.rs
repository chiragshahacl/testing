use std::time::Duration;

use flume::Sender;
use reqwest::Client;
use serde_json::json;
use tokio::time::sleep;
use tokio_util::sync::CancellationToken;
use tracing::{error, info, warn};

use crate::utils::{AppConfig, Commit};

use super::VitalsRecords;

pub struct VitalsFlusher {
    config: AppConfig,
    records: VitalsRecords,
    http_client: Client,
    commit_sender: Sender<Commit>,
}

impl VitalsFlusher {
    pub fn new(records: VitalsRecords, commit_sender: Sender<Commit>, config: AppConfig) -> Self {
        Self {
            records,
            config,
            http_client: Client::new(),
            commit_sender,
        }
    }

    async fn commit(&self) {
        let mut commits;
        {
            let mut records = self.records.lock().unwrap();
            commits = Vec::with_capacity(records.len());
            for message in records.values() {
                commits.push(Commit::from(message));
            }
            records.clear();
        }

        for commit in commits {
            match self.commit_sender.send_async(commit).await {
                Ok(_) => {}
                Err(e) => error!("Sending commit information to channel failed: {e}"),
            }
        }
    }

    fn generate_payloads(&self) -> Option<Vec<serde_json::Value>> {
        let records = self.records.lock().unwrap();

        if records.len() == 0 {
            return None;
        }

        let mut payloads = Vec::with_capacity(records.len());
        info!("Flushing {len} messages 🙏", len = records.len());

        for m in records.values() {
            let message_payload = &m.payload.payload;
            let observation = json!({
                "patient_primary_identifier": message_payload.patient_primary_identifier,
                "unit_code": message_payload.unit_code,
                "code": message_payload.code,
                "device_code": message_payload.device_code,
                "datapoints": message_payload.samples,
                "timestamp": format!("{}", message_payload.determination_time.format("%Y%m%d%H%M%S")),
                "device_primary_identifier": message_payload.device_primary_identifier
            });
            payloads.push(observation);
        }

        Some(payloads)
    }

    pub async fn process(self, cancellation_token: CancellationToken) {
        info!("🫡 Starting work");
        info!(
            "Flushing every {} seconds",
            self.config.vitals_flush_timeout_seconds
        );
        loop {
            tokio::select! {
                _ = sleep(Duration::from_secs(self.config.vitals_flush_timeout_seconds)) => {
                    if let Some(payloads) = self.generate_payloads() {
                        match self
                            .http_client
                            .post(&self.config.vitals_flush_endpoint)
                            .json(&payloads)
                            .send()
                            .await
                        {
                            Ok(_) => self.commit().await,
                            Err(e) => {
                                // In case of error, the message buffer won't be cleared,
                                // we will try to insert again
                                error!("Error while flushing messages: {e}");
                            }
                        };
                    }
                }
                _ = cancellation_token.cancelled() => {
                    warn!("🔌 Shutdown signal received, gracefully shutting down...");
                    self.commit().await;
                    break;
                }
            }
        }
        warn!("Shutdown");
    }
}
