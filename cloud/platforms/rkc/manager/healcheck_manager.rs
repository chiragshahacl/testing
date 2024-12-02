use crate::utils::{start_healthcheck, HealthState};
use flume::Receiver;
use tokio::task::JoinHandle;
use tokio_util::sync::CancellationToken;
use tracing::{info_span, Instrument};

pub fn spawn_healthcheck(
    cancellation_token: &CancellationToken,
    heartbeat_rx: Receiver<HealthState>,
) -> JoinHandle<()> {
    tokio::spawn(
        start_healthcheck(cancellation_token.clone(), heartbeat_rx)
            .instrument(info_span!("[Healthcheck 🩺]")),
    )
}
