use tokio::signal::unix::{signal, SignalKind};
use tokio::task::JoinHandle;
use tokio_util::sync::CancellationToken;
use tracing::{info, warn, Instrument};

pub fn spawn_termination_signal_task(cancellation_token: CancellationToken) -> JoinHandle<()> {
    tokio::spawn(
        async move {
            info!("Staring listening to termination signals");
            let mut sigterm =
                signal(SignalKind::terminate()).expect("Creating sigterm signal failed");
            let mut sigint =
                signal(SignalKind::interrupt()).expect("Creating sigint signal failed");

            tokio::select! {
                _ = sigterm.recv() => {
                    warn!("SIGTERM received!");
                },
                _ = sigint.recv() => {
                    warn!("SIGINT received!");
                },
            };
            warn!("🛑 Shutdown signal received!");

            cancellation_token.cancel();
            warn!("Shutdown");
        }
        .instrument(tracing::info_span!("[Signal Listener 📡]")),
    )
}
