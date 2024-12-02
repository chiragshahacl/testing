use flume::Receiver;
use rdkafka::message::OwnedMessage;
use tokio::task::JoinHandle;
use tokio_util::sync::CancellationToken;
use tracing::Instrument;
use tracing::{info, warn};

use crate::{
    processor::{Processor, VitalsExport, VitalsRecords},
    utils::AppConfig,
};

pub fn spawn_vitals_exporter(
    records: VitalsRecords,
    rx: Receiver<OwnedMessage>,
    config: &AppConfig,
    cancellation_token: &CancellationToken,
) -> Vec<JoinHandle<()>> {
    if !config.vitals_export_enabled {
        warn!("Vitals export is disabled, to enable it change the environment variable VITALS_EXPORT_ENABLED");

        return vec![];
    }

    info!(
        "🪄 Spawning {} Vitals Export Workers",
        config.vitals_export_workers
    );
    let mut handles = vec![];
    for i in 0..config.vitals_export_workers {
        let processor = VitalsExport::new(records.clone(), rx.clone(), config.clone())
            .process(cancellation_token.clone());

        let processor_handle = tokio::spawn(
            processor.instrument(tracing::info_span!("[HTTP export Worker 👷]", id = i)),
        );
        handles.push(processor_handle);
    }

    handles
}
