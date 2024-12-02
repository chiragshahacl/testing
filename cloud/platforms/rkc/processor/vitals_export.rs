use std::collections::HashMap;

use std::sync::{Arc, Mutex};
use tokio_util::sync::CancellationToken;
use tracing::{error, info, warn};

use crate::utils::{AppConfig, KafkaMessage};
use flume::Receiver;
use rdkafka::message::OwnedMessage;

use crate::Processor;

pub type VitalsRecords = Arc<Mutex<HashMap<String, KafkaMessage>>>;

pub struct VitalsExport {
    rx: Receiver<OwnedMessage>,
    _config: AppConfig,
    records: VitalsRecords,
}

impl Processor for VitalsExport {
    fn new(records: VitalsRecords, rx: Receiver<OwnedMessage>, config: AppConfig) -> Self {
        Self {
            records,
            rx,
            _config: config,
        }
    }

    async fn process(self, cancellation_token: CancellationToken) {
        info!("🫡 Starting work");

        loop {
            tokio::select! {
                result = self.rx.recv_async() => {
                    match result {
                        Ok(msg) => {
                            match KafkaMessage::try_from(msg) {
                                Ok(m) => {
                                    if m.payload.event_type == "NEW_METRICS" {
                                        self.store_message(m);
                                    }
                                },
                                Err(e) => {
                                    error!("Ignoring message due to parsing error: {e:?}");
                                    continue;
                                }
                            };
                        },
                        Err(e) => {
                            error!("Error receiving message {e:?}");
                            continue;
                        },
                    };

                }
                _ = cancellation_token.cancelled() => {
                    warn!("🔌 Shutdown signal received, gracefully shutting down...");
                    break;
                }
            }
        }
        warn!("Shutdown");
    }
}

impl VitalsExport {
    fn store_message(&self, message: KafkaMessage) {
        let key = &message.payload.key();
        let mut records = self.records.lock().unwrap();

        match records.get(key) {
            Some(existing_record) => {
                if existing_record.payload.payload.determination_time
                    < message.payload.payload.determination_time
                {
                    records.insert(key.to_string(), message);
                }
            }
            None => {
                records.insert(key.to_string(), message);
            }
        };
    }
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use chrono::NaiveDateTime;
    use rdkafka::Timestamp;
    use serde_json::json;
    use tokio::time::sleep;

    use crate::utils::{VitalsMessage, VitalsMessagePayload};

    use super::*;

    #[tokio::test]
    async fn can_be_cancelled() {
        let config = AppConfig::default();
        let (_tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let cancellation_token = CancellationToken::new();

        let processor = VitalsExport::new(records.clone(), rx, config);

        async fn cancel(cancellation_token: CancellationToken) {
            sleep(Duration::from_millis(100)).await;
            cancellation_token.cancel();
        }

        tokio::join!(
            processor.process(cancellation_token.clone()),
            cancel(cancellation_token),
        );
    }

    #[tokio::test]
    async fn stores_messages_coming_from_channel() {
        let config = AppConfig::default();
        let (tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let cancellation_token = CancellationToken::new();

        let processor = VitalsExport::new(records.clone(), rx, config);

        let payload = json!({
          "event_type": "NEW_METRICS",
          "timestamp": "2000-01-01 12:00:00.000000",
          "payload": {
            "patient_primary_identifier": "pid",
            "samples": ["123"],
            "determination_time": "2024-04-18T14:16:50.956",
            "code": "code",
            "device_code": "device-code",
            "unit_code": "unit-code",
            "device_primary_identifier": "dpi"
          }
        })
        .to_string()
        .as_bytes()
        .to_vec();

        let message = OwnedMessage::new(
            Some(payload),
            Some(vec![107, 101, 121]),
            String::from("topic"),
            Timestamp::CreateTime(0),
            0,
            0,
            None,
        );
        tx.send_async(message).await.unwrap();

        async fn cancel(cancellation_token: CancellationToken) {
            cancellation_token.cancel();
        }

        tokio::join!(
            processor.process(cancellation_token.clone()),
            cancel(cancellation_token),
        );

        let records = records.lock().unwrap();
        assert_eq!(records.len(), 1);
        assert!(records.contains_key("patient:pid~code:code~device:dpi"));
    }

    #[tokio::test]
    async fn ignores_non_new_metrics_event_types() {
        let config = AppConfig::default();
        let (tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let cancellation_token = CancellationToken::new();

        let processor = VitalsExport::new(records.clone(), rx, config);

        let payload = json!({
          "event_type": "FOO_BAR",
          "timestamp": "2000-01-01 12:00:00.000000",
          "payload": {
            "patient_primary_identifier": "pid",
            "samples": ["123"],
            "determination_time": "2024-04-18T14:16:50.956",
            "code": "code",
            "device_code": "device-code",
            "unit_code": "unit-code",
            "device_primary_identifier": "dpi"
          }
        })
        .to_string()
        .as_bytes()
        .to_vec();

        let message = OwnedMessage::new(
            Some(payload),
            Some(vec![107, 101, 121]),
            String::from("topic"),
            Timestamp::CreateTime(0),
            0,
            0,
            None,
        );
        tx.send_async(message).await.unwrap();

        async fn cancel(cancellation_token: CancellationToken) {
            cancellation_token.cancel();
        }

        tokio::join!(
            processor.process(cancellation_token.clone()),
            cancel(cancellation_token),
        );

        let records = records.lock().unwrap();
        assert_eq!(records.len(), 0);
    }

    #[test]
    fn store_new_record() {
        let config = AppConfig::default();
        let (_tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let message = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".to_string(),
                    code: "code".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T12:00:00.000Z",
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "device-primary-identifier".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };
        let processor = VitalsExport::new(records.clone(), rx, config);

        processor.store_message(message.clone());

        let records = records.lock().unwrap();

        assert!(records.contains_key(&message.payload.key()));
        assert_eq!(records.len(), 1);
        assert_eq!(
            records
                .get(&message.payload.key())
                .unwrap()
                .payload
                .payload
                .determination_time
                .to_string(),
            "2020-01-01 12:00:00"
        );
    }

    #[test]
    fn overwrite_existing_record_with_newer_message() {
        let config = AppConfig::default();
        let (_tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let message = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".to_string(),
                    code: "code".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T12:00:00.000Z", // noon
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "device-primary-identifier".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };
        let processor = VitalsExport::new(records.clone(), rx, config);

        processor.store_message(message.clone());

        let message = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".to_string(),
                    code: "code".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T13:00:00.000Z", // an hour later
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "device-primary-identifier".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };
        processor.store_message(message.clone());

        let records = records.lock().unwrap();

        assert!(records.contains_key(&message.payload.key()));
        assert_eq!(
            records
                .get(&message.payload.key())
                .unwrap()
                .payload
                .payload
                .determination_time
                .to_string(),
            "2020-01-01 13:00:00"
        );
    }

    #[test]
    fn avoids_overwritting_existing_record_with_older_message() {
        let config = AppConfig::default();
        let (_tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let message = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".to_string(),
                    code: "code".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T12:00:00.000Z", // noon
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "device-primary-identifier".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };
        let processor = VitalsExport::new(records.clone(), rx, config);

        processor.store_message(message.clone());

        let message = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".to_string(),
                    code: "code".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T11:00:00.000Z", // an hour earlier
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "device-primary-identifier".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };
        processor.store_message(message.clone());

        let records = records.lock().unwrap();

        assert!(records.contains_key(&message.payload.key()));
        assert_eq!(
            records
                .get(&message.payload.key())
                .unwrap()
                .payload
                .payload
                .determination_time
                .to_string(),
            "2020-01-01 12:00:00"
        );
    }

    #[test]
    fn stores_multiple_records() {
        let config = AppConfig::default();
        let (_tx, rx) = flume::unbounded::<OwnedMessage>();
        let records = VitalsRecords::new(Mutex::new(HashMap::new()));
        let message1 = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid1".to_string(),
                    code: "code1".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T12:00:00.000Z",
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "dpi1".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };

        let message2 = KafkaMessage {
            payload: VitalsMessage {
                event_type: "event-type".to_string(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid2".to_string(),
                    code: "code2".to_string(),
                    samples: vec![1, 2, 3].into(),
                    determination_time: NaiveDateTime::parse_from_str(
                        "2020-01-01T12:00:00.000Z",
                        "%Y-%m-%dT%H:%M:%S%.3fZ",
                    )
                    .unwrap(),
                    device_code: "device-code".to_string(),
                    unit_code: Some("unit-code".to_string()),
                    device_primary_identifier: "dpi2".to_string(),
                },
            },
            key: "key".to_string(),
            topic: "topic".to_string(),
            offset: 123,
            partition: 0,
        };

        let processor = VitalsExport::new(records.clone(), rx, config);
        processor.store_message(message1.clone());
        processor.store_message(message2.clone());

        let records = records.lock().unwrap();

        assert_eq!(records.len(), 2);
        assert!(records.contains_key("patient:pid1~code:code1~device:dpi1"));
        assert!(records.contains_key("patient:pid2~code:code2~device:dpi2"));
    }
}
