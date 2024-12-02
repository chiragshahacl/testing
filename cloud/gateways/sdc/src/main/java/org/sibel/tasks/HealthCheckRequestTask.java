package org.sibel.tasks;

import java.io.IOException;
import java.net.Socket;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class HealthCheckRequestTask implements Runnable {
    private static final Logger LOG = LogManager.getLogger();

    private final Socket clientSocket;
    private final boolean isHealthy;
    private final String errorMessage;

    public HealthCheckRequestTask(Socket clientSocket, boolean isHealthy, String errorMessage) {
        this.clientSocket = clientSocket;
        this.isHealthy = isHealthy;
        this.errorMessage = errorMessage;
    }

    public void run() {
        try {
            clientSocket.getInputStream();
            var output = clientSocket.getOutputStream();
            var response = isHealthy
                    ? getResponse(200, "OK", "Healthy")
                    : getResponse(500, "Internal Server Error", errorMessage);
            output.write(response.getBytes());
            output.flush();
            output.close();
        } catch (IOException e) {
            LOG.error("Error processing health check request", e);
        }
    }

    private String getResponse(int status, String statusText, String message) {
        var body = getResponseBody(message);
        var headers = getResponseHeaders(status, statusText, body.length());
        return "%s\r\n%s".formatted(headers, body);
    }

    private String getResponseHeaders(int status, String statusText, int bodyLength) {
        return """
                HTTP/1.1 %d %s\r
                Content-Type: text/html\r
                Content-Length: %d\r
                """
                .formatted(status, statusText, bodyLength);
    }

    private String getResponseBody(String message) {
        return """
            <html>
                <head>
                    <title>Health Check</title>
                </head>
                <body>
                    <pre>%s</pre>
                </body>
            </html>"""
                .formatted(message);
    }
}
