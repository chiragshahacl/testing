use flume::Sender;
use tokio::task::JoinHandle;
use tokio_util::sync::CancellationToken;
use tracing::info;
use tracing::Instrument;

use crate::processor::VitalsFlusher;
use crate::utils::Commit;
use crate::{processor::VitalsRecords, utils::AppConfig};

pub fn spawn_vitals_flusher(
    records: VitalsRecords,
    tx: Sender<Commit>,
    config: &AppConfig,
    cancellation_token: &CancellationToken,
) -> JoinHandle<()> {
    info!("🪄 Spawning a Vitals Flush Worker",);

    tokio::spawn(
        VitalsFlusher::new(records.clone(), tx, config.clone())
            .process(cancellation_token.clone())
            .instrument(tracing::info_span!("[HTTP Flush Worker 👷]")),
    )
}
