use flume::Receiver;
use rdkafka::message::OwnedMessage;

mod vitals_export;
mod vitals_flusher;

use crate::utils::AppConfig;
use tokio_util::sync::CancellationToken;
pub use vitals_export::{VitalsExport, VitalsRecords};
pub use vitals_flusher::VitalsFlusher;

pub trait Processor {
    fn new(records: VitalsRecords, rx: Receiver<OwnedMessage>, config: AppConfig) -> Self;
    fn process(
        self,
        cancellation_token: CancellationToken,
    ) -> impl std::future::Future<Output = ()> + Send;
}
