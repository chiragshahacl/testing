package org.sibel.di;

import com.google.inject.*;
import com.google.inject.assistedinject.FactoryModuleBuilder;
import com.google.inject.name.Named;
import com.google.inject.name.Names;
import io.lettuce.core.api.sync.RedisCommands;
import java.util.UUID;
import java.util.concurrent.*;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.ExtendedExecutor;
import org.sibel.PatientMonitor;
import org.sibel.apis.*;
import org.sibel.apis.auth.JWTAuth;
import org.sibel.apis.auth.JWTAuthImpl;
import org.sibel.apis.auth.RSAKeyProvider;
import org.sibel.apis.auth.RSAKeyProviderImpl;
import org.sibel.config.Settings;
import org.sibel.constants.DI;
import org.sibel.consumers.KafkaMessageConsumer;
import org.sibel.consumers.KafkaMessageConsumerImpl;
import org.sibel.dataProcessors.*;
import org.sibel.dataProcessors.utils.Cache;
import org.sibel.dataProcessors.utils.InMemoryCache;
import org.sibel.dataProcessors.utils.NoCache;
import org.sibel.exceptions.RedisUnavailable;
import org.sibel.factories.*;
import org.sibel.factories.ProcessorFactory;
import org.sibel.models.payloads.AlertPayload;
import org.sibel.models.payloads.internal.VitalsRangePayload;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.producers.KafkaMessageProducerImpl;
import org.sibel.repositories.PatientMonitorRepository;
import org.sibel.repositories.PatientMonitorRepositoryImpl;
import org.sibel.tasks.*;
import org.sibel.utils.CacheClient;
import org.sibel.utils.CacheClientImpl;
import org.somda.sdc.dpws.client.Client;

public class ConsumerModule extends AbstractModule {
    private static final Logger LOG = LogManager.getLogger();

    @Override
    protected void configure() {
        bind(Callable.class).annotatedWith(Names.named(DI.HEALTH_CHECK_TASK)).to(HealthCheckServiceTask.class);
        bind(PatientApi.class).to(PatientApiImpl.class);
        bind(EhrApi.class).to(EhrApiImpl.class);
        bind(DeviceApi.class).to(DeviceApiImpl.class);
        bind(UuidProvider.class).to(UuidProviderImpl.class);
        bind(InstantProvider.class).to(InstantProviderImpl.class);

        // Singletons
        bind(CacheClient.class).to(CacheClientImpl.class).in(Scopes.SINGLETON);
        bind(PatientMonitorRepository.class)
                .to(PatientMonitorRepositoryImpl.class)
                .in(Scopes.SINGLETON);
        bind(JWTAuth.class).to(JWTAuthImpl.class).in(Scopes.SINGLETON);
        bind(RSAKeyProvider.class).to(RSAKeyProviderImpl.class).in(Scopes.SINGLETON);
        bind(CoordinatorTask.class).to(CoordinatorTaskImpl.class).in(Scopes.SINGLETON);
        bind(KafkaMessageProducer.class).to(KafkaMessageProducerImpl.class).in(Scopes.SINGLETON);
        bind(KafkaMessageConsumer.class).to(KafkaMessageConsumerImpl.class).in(Scopes.SINGLETON);

        // Factories
        install(new FactoryModuleBuilder()
                .implement(AlertChangeProcessor.class, AlertChangeProcessor.class)
                .implement(ComponentStateChangeProcessor.class, ComponentStateChangeProcessor.class)
                .implement(MetricChangeProcessor.class, MetricChangeProcessor.class)
                .implement(PatientContextChangeProcessor.class, PatientContextChangeProcessor.class)
                .implement(VitalRangeProcessor.class, VitalRangeProcessor.class)
                .implement(WaveformChangeProcessor.class, WaveformChangeProcessor.class)
                .build(ProcessorFactory.class));
        install(new FactoryModuleBuilder()
                .implement(ConsumerReportProcessor.class, ConsumerReportProcessor.class)
                .build(ConsumerReportProcessorFactory.class));
        install(new FactoryModuleBuilder()
                .implement(PatientMonitor.class, PatientMonitor.class)
                .build(PatientMonitorFactory.class));
        install(new FactoryModuleBuilder()
                .implement(DeviceConnectionCheckTask.class, DeviceConnectionCheckTask.class)
                .build(TaskFactory.class));

        // Other modules
        install(new GsonModule());
    }

    @Provides
    public RedisCommands<String, String> getRedisCommands(Injector injector) {
        try {
            return injector.getInstance(CacheClient.class).getRedisCommands();
        } catch (RedisUnavailable e) {
            LOG.error("Failed to connect with Redis", e);
            throw new RuntimeException(e);
        }
    }

    @Provides
    @Singleton
    @Named(DI.CONSUMER_ID)
    public String getConsumerId() {
        return UUID.randomUUID().toString();
    }

    @Provides
    @Singleton
    @Named(DI.CLIENT)
    public Client getClient(Injector injector) {
        return injector.getInstance(Client.class);
    }

    @Provides
    @Singleton
    @Named(DI.ALERT_CACHE)
    public Cache<AlertPayload> getAlertsCache(Injector injector) {
        var settings = injector.getInstance(Settings.class);
        return settings.ALERTS_CACHE_ENABLED() ? new InMemoryCache<>() : new NoCache<>();
    }

    @Provides
    @Singleton
    @Named(DI.VITALS_CACHE)
    public Cache<VitalsRangePayload> getVitalsCache(Injector injector) {
        var settings = injector.getInstance(Settings.class);
        return settings.VITALS_CACHE_ENABLED() ? new InMemoryCache<>() : new NoCache<>();
    }

    @Provides
    @Singleton
    public ExecutorService getExecutor() {
        return new ExtendedExecutor();
    }
}
