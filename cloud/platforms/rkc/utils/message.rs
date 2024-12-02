use chrono::NaiveDateTime;
use rdkafka::message::{Message, OwnedMessage};
use serde_derive::{Deserialize, Serialize};
use serde_json::Value;
use std::str;

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct VitalsMessagePayload {
    pub patient_primary_identifier: String,
    pub code: String,
    pub samples: Value,
    pub determination_time: NaiveDateTime,
    pub device_code: String,
    pub unit_code: Option<String>,
    pub device_primary_identifier: String,
}

#[derive(Serialize, Deserialize, PartialEq, Clone, Debug)]
pub struct VitalsMessage {
    pub event_type: String,
    pub payload: VitalsMessagePayload,
}

#[derive(Debug, Clone)]
pub struct KafkaMessage {
    pub payload: VitalsMessage,
    pub key: String,
    pub topic: String,
    pub offset: i64,
    pub partition: i32,
}

impl VitalsMessage {
    pub fn key(&self) -> String {
        format!(
            "patient:{}~code:{}~device:{}",
            self.payload.patient_primary_identifier,
            self.payload.code,
            self.payload.device_primary_identifier
        )
    }
}

impl TryFrom<OwnedMessage> for KafkaMessage {
    type Error = String;

    fn try_from(val: OwnedMessage) -> Result<Self, Self::Error> {
        let payload = match val.payload() {
            Some(m) => m,
            None => {
                return Err("Empty payload".to_string());
            }
        };

        let payload_str = match str::from_utf8(payload) {
            Ok(m) => m,
            Err(e) => return Err(e.to_string()),
        };

        let payload_hash: VitalsMessage = match serde_json::from_str(payload_str) {
            Ok(m) => m,
            Err(e) => return Err(e.to_string()),
        };

        let key = match val.key() {
            Some(k) => String::from_utf8_lossy(k).to_string(),
            None => {
                return Err("Missing message key".into());
            }
        };

        Ok(KafkaMessage {
            payload: payload_hash,
            key,
            partition: val.partition(),
            offset: val.offset(),
            topic: String::from(val.topic()),
        })
    }
}

#[cfg(test)]
mod tests {
    use std::str::FromStr;

    use super::*;
    use rdkafka::{message::OwnedHeaders, Timestamp};
    use serde_json::json;

    #[test]
    fn parse_empty_payload() {
        let message = OwnedMessage::new(
            None,
            Some(vec![]),
            String::from("topic"),
            Timestamp::CreateTime(0),
            0,
            0,
            None,
        );

        let result = KafkaMessage::try_from(message);

        let error = match result {
            Ok(_) => panic!("Error expected"),
            Err(e) => e,
        };

        assert_eq!(error, "Empty payload");
    }

    #[test]
    fn parse_invalid_payload() {
        let message = OwnedMessage::new(
            Some(vec![]),
            Some(vec![]),
            String::from("topic"),
            Timestamp::CreateTime(0),
            0,
            0,
            None,
        );

        let result = KafkaMessage::try_from(message);

        let error = match result {
            Ok(_) => panic!("Error expected"),
            Err(e) => e,
        };

        assert_eq!(error, "EOF while parsing a value at line 1 column 0");
    }

    #[test]
    fn parse_missing_key() {
        let payload = json!({
          "event_type": "event-type",
          "timestamp": "2000-01-01 12:00:00.000000",
          "payload": {
            "patient_primary_identifier": "pid",
            "samples": ["123"],
            "determination_time": "2024-04-18T14:16:50.956",
            "code": "code",
            "device_code": "device-code",
            "unit_code": "unit-code",
            "device_primary_identifier": "device pid"
          }
        })
        .to_string()
        .as_bytes()
        .to_vec();

        let headers = OwnedHeaders::new();
        let message = OwnedMessage::new(
            Some(payload),
            None,
            String::from("topic"),
            Timestamp::CreateTime(0),
            0,
            0,
            Some(headers),
        );

        let result = KafkaMessage::try_from(message);

        let error = match result {
            Ok(_) => panic!("Error expected"),
            Err(e) => e,
        };

        assert_eq!(error, "Missing message key");
    }

    #[test]
    fn parse_valid_owned_message() {
        let headers = OwnedHeaders::new();

        let payload = json!({
          "event_type": "event-type",
          "timestamp": "2000-01-01 12:00:00.000000",
          "payload": {
            "patient_primary_identifier": "pid",
            "samples": ["123"],
            "determination_time": "2024-04-18T14:16:50.956",
            "code": "code",
            "device_code": "device-code",
            "unit_code": "unit-code",
            "device_primary_identifier": "device pid"
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
            Some(headers),
        );

        let result = KafkaMessage::try_from(message);

        assert!(result.is_ok());

        assert_eq!(
            result.unwrap().payload,
            VitalsMessage {
                event_type: "event-type".into(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".into(),
                    samples: vec!("123").into(),
                    determination_time: NaiveDateTime::from_str("2024-04-18T14:16:50.956").unwrap(),
                    code: "code".into(),
                    device_code: "device-code".into(),
                    unit_code: Some("unit-code".into()),
                    device_primary_identifier: "device pid".into()
                }
            }
        );
    }

    #[test]
    fn parse_valid_owned_message_missing_unit_code() {
        let headers = OwnedHeaders::new();

        let payload = json!({
          "event_type": "event-type",
          "timestamp": "2000-01-01 12:00:00.000000",
          "payload": {
            "patient_primary_identifier": "pid",
            "samples": ["123"],
            "determination_time": "2024-04-18T14:16:50.956",
            "code": "code",
            "device_code": "device-code",
            // no unit code here
            "device_primary_identifier": "device pid"
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
            Some(headers),
        );

        let result = KafkaMessage::try_from(message);

        assert!(result.is_ok());

        assert_eq!(
            result.unwrap().payload,
            VitalsMessage {
                event_type: "event-type".into(),
                payload: VitalsMessagePayload {
                    patient_primary_identifier: "pid".into(),
                    samples: vec!("123").into(),
                    determination_time: NaiveDateTime::from_str("2024-04-18T14:16:50.956").unwrap(),
                    code: "code".into(),
                    device_code: "device-code".into(),
                    unit_code: None,
                    device_primary_identifier: "device pid".into()
                }
            }
        );
    }

    #[test]
    fn parse_valid_key() {
        let payload = json!({
          "event_type": "event-type",
          "timestamp": "2000-01-01 12:00:00.000000",
          "payload": {
            "patient_primary_identifier": "pid",
            "samples": ["123"],
            "determination_time": "2024-04-18T14:16:50.956",
            "code": "code",
            "device_code": "device-code",
            "unit_code": "unit-code",
            "device_primary_identifier": "device pid"
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

        let result = KafkaMessage::try_from(message);

        assert!(result.is_ok());

        assert_eq!(result.unwrap().key, "key");
    }
}
