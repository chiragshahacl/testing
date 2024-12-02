export const waitForOpenConnection = (socket: WebSocket) => {
  return new Promise<void>((resolve, reject) => {
    const maxNumberOfAttempts = 10;
    const intervalTime = 200; // ms

    let currentAttempt = 0;
    const interval = setInterval(() => {
      if (currentAttempt > maxNumberOfAttempts - 1) {
        clearInterval(interval);
        reject(new Error('Maximum number of attempts exceeded'));
      } else if (socket.readyState === socket.OPEN) {
        clearInterval(interval);
        resolve();
      }
      currentAttempt++;
    }, intervalTime);
  });
};

/**
 * Sends a specific message through a Websocket if open, and if not it tries to open it
 * and immediately send the message
 */
export const sendWebsocketMessage = async (socket: WebSocket, msg: string) => {
  if (socket.readyState !== socket.OPEN) {
    try {
      await waitForOpenConnection(socket);
      socket.send(msg);
    } catch (e) {
      /* empty */
    }
  } else {
    socket.send(msg);
  }
};
