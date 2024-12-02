use super::KafkaMessage;

#[derive(Debug)]
pub struct Commit {
    pub partition: i32,
    pub offset: i64,
    pub topic: String,
}

impl From<&KafkaMessage> for Commit {
    fn from(value: &KafkaMessage) -> Self {
        Commit {
            partition: value.partition,
            offset: value.offset,
            topic: value.topic.clone(),
        }
    }
}
