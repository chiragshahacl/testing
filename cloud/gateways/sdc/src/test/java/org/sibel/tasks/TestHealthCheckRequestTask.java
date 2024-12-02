package org.sibel.tasks;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.*;

import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.ArgumentCaptor;

class TestHealthCheckRequestTask {

    private final Socket socket = mock();
    private final OutputStream outputStreamMock = mock();

    @BeforeEach
    void setUp() throws IOException {
        reset(socket, outputStreamMock);
        when(socket.getOutputStream()).thenReturn(outputStreamMock);
    }

    public static Stream<Arguments> testHealth() {
        return Stream.of(
                Arguments.arguments(
                        true,
                        null,
                        """
                        HTTP/1.1 200 OK\r
                        Content-Type: text/html\r
                        Content-Length: 123\r
                        \r
                        <html>
                            <head>
                                <title>Health Check</title>
                            </head>
                            <body>
                                <pre>Healthy</pre>
                            </body>
                        </html>"""),
                Arguments.arguments(
                        false,
                        "TEST ERROR",
                        """
                        HTTP/1.1 500 Internal Server Error\r
                        Content-Type: text/html\r
                        Content-Length: 126\r
                        \r
                        <html>
                            <head>
                                <title>Health Check</title>
                            </head>
                            <body>
                                <pre>TEST ERROR</pre>
                            </body>
                        </html>"""));
    }

    @ParameterizedTest
    @MethodSource
    void testHealth(boolean isHealthy, String errorMessage, String expectedResponse) throws IOException {
        new HealthCheckRequestTask(socket, isHealthy, errorMessage).run();

        var captor = ArgumentCaptor.forClass(byte[].class);
        verify(outputStreamMock).write(captor.capture());
        var actualResponse = new String(captor.getValue(), StandardCharsets.UTF_8);

        assertEquals(expectedResponse, actualResponse);
    }
}
