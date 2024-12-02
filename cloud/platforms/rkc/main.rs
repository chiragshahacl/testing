mod consumer;
use std::{collections::HashMap, sync::Mutex};
mod manager;
mod processor;
mod utils;

use crate::utils::{AppConfig, HealthState};
use manager::{
    spawn_consumer, spawn_healthcheck, spawn_termination_signal_task, spawn_vitals_exporter,
    spawn_vitals_flusher,
};
use processor::{Processor, VitalsRecords};
use rdkafka::message::OwnedMessage;
use tokio_util::sync::CancellationToken;
use utils::Commit;

async fn run() {
    let config = AppConfig::default();

    // Init logger on INFO by default, set RUST_LOG env var to TRACE/DEBUG/INFO/etc to change
    let format = tracing_subscriber::fmt::format()
        .with_target(false)
        .compact();
    tracing_subscriber::fmt().event_format(format).init();

    // Start MPMC channel
    let (tx, rx) = flume::unbounded::<OwnedMessage>();
    let (commit_tx, commit_rx) = flume::unbounded::<Commit>();

    let cancellation_token = CancellationToken::new();

    let (heartbeat_tx, heartbeat_rx) = flume::unbounded::<HealthState>();
    let records = VitalsRecords::new(Mutex::new(HashMap::new()));

    let consumer_task = spawn_consumer(&config, tx, commit_rx, &cancellation_token, heartbeat_tx);
    let vitals_export_task =
        spawn_vitals_exporter(records.clone(), rx.clone(), &config, &cancellation_token);
    let healthcheck_task = spawn_healthcheck(&cancellation_token, heartbeat_rx);
    let termination_signal_task = spawn_termination_signal_task(cancellation_token.clone());
    let flush_worker =
        spawn_vitals_flusher(records.clone(), commit_tx, &config, &cancellation_token);

    let mut handles = vec![
        consumer_task,
        healthcheck_task,
        termination_signal_task,
        flush_worker,
    ];
    handles.extend(vitals_export_task);

    futures::future::join_all(handles).await;

    std::process::exit(1);
}

fn main() {
    let config = AppConfig::default();

    let _sentry = sentry::init((
        config.sentry_dsn,
        sentry::ClientOptions {
            traces_sample_rate: config.sentry_trace_sample_rate,
            debug: config.debug,
            environment: Some(config.environment.into()),
            release: Some(config.sibel_version.into()),
            ..Default::default()
        },
    ));

    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("Tokio runtime failed")
        .block_on(run());
}
