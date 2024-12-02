use std::sync::{Arc, Mutex};

use flume::Receiver;
use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::{TcpListener, TcpStream},
};
use tracing::{debug, error, info, warn};

use tokio::join;
use tokio_util::sync::CancellationToken;

#[derive(Clone, Debug)]
pub enum HealthState {
    Healthy,
    Unhealthy(String),
}

#[derive(Debug)]
struct _AppState {
    health_state: Mutex<HealthState>,
}

type AppState = Arc<_AppState>;

async fn process_socket(socket: &mut TcpStream, state: AppState) {
    let mut buf = [0u8; 4096];
    let _ = socket.read(&mut buf).await.unwrap();

    let response_str = match &*state.health_state.lock().unwrap() {
        HealthState::Healthy => {
            "HTTP/1.1 200 OK

<!DOCTYPE html>
<html lang=\"en\">
<body>
Healthy <span>&#10084;</span>
</body>
</html>"
        }
        _ => {
            "HTTP/1.1 500 internal server error

<!DOCTYPE html>
<html lang=\"en\">
<body>
Unhealthy <span>&#9760;</span>
</body>
</html>"
        }
    };
    socket.write_all(response_str.as_bytes()).await.unwrap();
    socket.flush().await.unwrap();
}
async fn run_server(state: AppState) {
    let listener = TcpListener::bind("0.0.0.0:8080").await.unwrap();

    loop {
        let (mut socket, _) = listener.accept().await.unwrap();
        process_socket(&mut socket, state.clone()).await;
    }
}

pub async fn start_healthcheck(
    cancellation_token: CancellationToken,
    heartbeat_rx: Receiver<HealthState>,
) {
    info!("Starting healthcheck");

    let state = Arc::new(_AppState {
        health_state: Mutex::new(HealthState::Healthy),
    });

    tokio::select! {
       _ = health_process(state, heartbeat_rx) => {}
       _ = cancellation_token.cancelled() => {
           warn!("🔌 Shutdown signal received, gracefully shutting down...");
       },
    }
    warn!("Shutdown");
}
async fn health_process(state: AppState, heartbeat_rx: Receiver<HealthState>) {
    let run_sv_handle = tokio::spawn(run_server(state.clone()));
    let set_health_handle = tokio::spawn(set_health_state(heartbeat_rx, state.clone()));

    let _ = join!(run_sv_handle, set_health_handle);
}

async fn set_health_state(receiver: Receiver<HealthState>, state: AppState) {
    loop {
        match receiver.recv_async().await {
            Ok(HealthState::Healthy) => {
                debug!("Received healthy state");
            }
            Ok(new_state) => {
                error!("Received unhealthy state: '{:?}'", new_state);
                let mut health_state = state.health_state.lock().unwrap();
                *health_state = new_state;
            }
            Err(_) => {}
        }
    }
}
