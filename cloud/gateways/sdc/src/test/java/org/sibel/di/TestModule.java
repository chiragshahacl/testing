package org.sibel.di;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.inject.*;
import com.google.inject.assistedinject.FactoryModuleBuilder;
import com.google.inject.name.Named;
import com.google.inject.name.Names;
import io.lettuce.core.api.sync.RedisCommands;
import java.util.concurrent.ExecutorService;
import org.sibel.PatientMonitor;
import org.sibel.TestConstants;
import org.sibel.apis.DeviceApi;
import org.sibel.apis.EhrApi;
import org.sibel.apis.PatientApi;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.consumers.KafkaMessageConsumer;
import org.sibel.dataProcessors.*;
import org.sibel.dataProcessors.utils.Cache;
import org.sibel.dataProcessors.utils.NoCache;
import org.sibel.factories.*;
import org.sibel.mocks.KafkaProducerMock;
import org.sibel.models.payloads.AlertPayload;
import org.sibel.models.payloads.internal.VitalsRangePayload;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.repositories.PatientMonitorRepository;
import org.sibel.repositories.PatientMonitorRepositoryImpl;
import org.sibel.tasks.ConsumerReportProcessor;
import org.sibel.tasks.DeviceConnectionCheckTask;
import org.sibel.utils.CacheClient;
import org.somda.sdc.dpws.client.Client;
import org.somda.sdc.glue.consumer.SdcRemoteDevicesConnector;

public class TestModule extends AbstractModule {
    @Override
    protected void configure() {
        // Inject mocks
        bind(KafkaMessageProducer.class).to(KafkaProducerMock.class).asEagerSingleton();
        bind(KafkaMessageConsumer.class).toInstance(mock());
        bind(PatientApi.class).toInstance(mock());
        bind(EhrApi.class).toInstance(mock());
        bind(DeviceApi.class).toInstance(mock());
        bind(UuidProvider.class).toInstance(mock());
        bind(InstantProvider.class).toInstance(mock());
        bind(Client.class).annotatedWith(Names.named(DI.CLIENT)).toInstance(mock());
        bind(SdcRemoteDevicesConnector.class).toInstance(mock());
        bind(Key.get(new TypeLiteral<RedisCommands<String, String>>() {})).toInstance(mock());
        bind(String.class).annotatedWith(Names.named(DI.CONSUMER_ID)).toInstance(TestConstants.CONSUMER_ID);
        bind(ExecutorService.class).toInstance(mock());
        bind(CacheClient.class).toInstance(mock());

        // Same
        install(new GsonModule(true));

        // Inject real code
        bind(PatientMonitorRepository.class)
                .to(PatientMonitorRepositoryImpl.class)
                .asEagerSingleton();
        install(new FactoryModuleBuilder()
                .implement(AlertChangeProcessor.class, AlertChangeProcessor.class)
                .implement(ComponentStateChangeProcessor.class, ComponentStateChangeProcessor.class)
                .implement(MetricChangeProcessor.class, MetricChangeProcessor.class)
                .implement(PatientContextChangeProcessor.class, PatientContextChangeProcessor.class)
                .implement(VitalRangeProcessor.class, VitalRangeProcessor.class)
                .implement(WaveformChangeProcessor.class, WaveformChangeProcessor.class)
                .build(ProcessorFactory.class));
        install(new FactoryModuleBuilder()
                .implement(PatientMonitor.class, PatientMonitor.class)
                .build(PatientMonitorFactory.class));
        install(new FactoryModuleBuilder()
                .implement(ConsumerReportProcessor.class, ConsumerReportProcessor.class)
                .build(ConsumerReportProcessorFactory.class));
        install(new FactoryModuleBuilder()
                .implement(DeviceConnectionCheckTask.class, DeviceConnectionCheckTask.class)
                .build(TaskFactory.class));
    }

    @Singleton
    @Provides
    Settings getSettingsMock() {
        Settings settings = mock();
        when(settings.KAFKA_TOPIC_DEVICE()).thenReturn(TestConstants.Settings.DEVICE_KAFKA_TOPIC);
        when(settings.KAFKA_TOPIC_VITALS()).thenReturn(TestConstants.Settings.VITALS_KAFKA_TOPIC);
        when(settings.KAFKA_TOPIC_ALERT()).thenReturn(TestConstants.Settings.ALERTS_KAFKA_TOPIC);
        when(settings.FEATURE_DETERMINATION_PERIOD_ENABLED())
                .thenReturn(TestConstants.Settings.DETERMINATION_PERIOD_ENABLED);
        when(settings.CENTRAL_HUB_VALIDATOR_ID()).thenReturn(TestConstants.Settings.CENTRAL_HUB_VALIDATOR_ID);
        when(settings.PATIENT_MONITOR_VALIDATOR_ID()).thenReturn(TestConstants.Settings.PATIENT_MONITOR_VALIDATOR_ID);
        return settings;
    }

    @Provides
    @Singleton
    @Named(DI.ALERT_CACHE)
    public Cache<AlertPayload> getAlertsCache() {
        return new NoCache<>();
    }

    @Provides
    @Singleton
    @Named(DI.VITALS_CACHE)
    public Cache<VitalsRangePayload> getVitalsCache() {
        return new NoCache<>();
    }
}
