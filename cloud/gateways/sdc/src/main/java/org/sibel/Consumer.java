package org.sibel;

import com.google.inject.Injector;
import com.google.inject.Key;
import com.google.inject.name.Names;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.constants.DI;
import org.sibel.mdib.overrides.CustomJaxbMarshalling;
import org.sibel.tasks.CoordinatorTask;
import org.sibel.utils.ConsumerUtil;
import org.somda.sdc.dpws.DpwsFramework;
import org.somda.sdc.dpws.client.Client;
import org.somda.sdc.glue.consumer.SdcRemoteDevicesConnector;

/**
 * This is an example consumer which matches in functionality
 * <p>
 * This consumer executes the following steps and prints whether each step was
 * successful
 * 1. discovery of device with specific endpoint
 * 2. connect to device with specific endpoint
 * 3. read mdib of provider
 * 4. subscribe metrics, alerts, waveforms
 * 5. check that least one patient context exists
 * 6. check that at least one location context exists
 * 7. check that the metric (see above) changes within 30 seconds at least 5
 * times
 * 8. check that the alert condition (see above)change within 30 seconds at
 * least 5 times
 * 9. execute operations (Activate, SetString, SetValue) as specified and check
 * that result is “finished”
 */
public class Consumer {

    private static final Logger LOG = LogManager.getLogger(Consumer.class);
    private final Client client;
    private final SdcRemoteDevicesConnector connector;
    private DpwsFramework dpwsFramework;
    private final Injector injector;
    private NetworkInterface networkInterface;

    /**
     * Creates an SDC Consumer instance.
     *
     * @param consumerUtil utility containing injector and settings
     * @throws SocketException      if network adapter couldn't be bound
     * @throws UnknownHostException if localhost couldn't be determined
     */
    public Consumer(ConsumerUtil consumerUtil) throws SocketException, UnknownHostException {
        this.injector = consumerUtil.getInjector();
        this.client = injector.getInstance(Key.get(Client.class, Names.named(DI.CLIENT)));
        this.connector = injector.getInstance(SdcRemoteDevicesConnector.class);
        if (consumerUtil.getIface() != null && !consumerUtil.getIface().isBlank()) {
            LOG.info("Starting with interface {}", consumerUtil.getIface());
            this.networkInterface = NetworkInterface.getByName(consumerUtil.getIface());
        } else {
            if (consumerUtil.getAddress() != null && !consumerUtil.getAddress().isBlank()) {
                // bind to adapter matching ip
                LOG.info("Starting with address {}", consumerUtil.getAddress());
                this.networkInterface =
                        NetworkInterface.getByInetAddress(InetAddress.getByName(consumerUtil.getAddress()));
            } else {
                // find loopback interface for fallback
                networkInterface = NetworkInterface.getByInetAddress(InetAddress.getLoopbackAddress());
                LOG.info("Starting with fallback default adapter {}", networkInterface);
            }
        }
    }

    public Client getClient() {
        return client;
    }

    public SdcRemoteDevicesConnector getConnector() {
        return connector;
    }

    protected void startUp() {
        // Init custom marshalling service needed to run MDPWS
        var customMarshallingService = injector.getInstance(CustomJaxbMarshalling.class);
        customMarshallingService.startAsync().awaitRunning();

        // provide the name of your network adapter
        this.dpwsFramework = injector.getInstance(DpwsFramework.class);
        this.dpwsFramework.setNetworkInterface(networkInterface);
        dpwsFramework.startAsync().awaitRunning();
        client.startAsync().awaitRunning();

        // Startup coordinator
        var executor = injector.getInstance(ExecutorService.class);
        executor.submit(injector.getInstance(CoordinatorTask.class));
    }

    protected void shutDown() {
        client.stopAsync().awaitTerminated();
        dpwsFramework.stopAsync().awaitTerminated();
    }

    public Injector getInjector() {
        return injector;
    }

    public static void main(String[] args) throws SocketException, UnknownHostException {
        var utilSettings = new ConsumerUtil(args);
        Injector injector = utilSettings.getInjector();

        var healthCheckTask =
                injector.getInstance(Key.get(Callable.class).withAnnotation(Names.named(DI.HEALTH_CHECK_TASK)));
        injector.getInstance(ExecutorService.class).submit(healthCheckTask);

        var consumer = new Consumer(utilSettings);
        consumer.startUp();

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            injector.getInstance(ExecutorService.class).shutdown();

            // TODO: Devices released
            LOG.info("TODO: Devices released");
        }));
    }
}
