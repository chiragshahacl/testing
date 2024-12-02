package org.sibel;

import static org.junit.jupiter.api.Assertions.fail;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.*;
import static org.sibel.constants.MdibHandles.getOperationHandle;

import com.google.common.util.concurrent.Futures;
import com.google.inject.Guice;
import com.google.inject.Injector;
import com.google.inject.Key;
import com.google.inject.TypeLiteral;
import io.lettuce.core.api.sync.RedisCommands;
import java.util.List;
import org.mockito.AdditionalAnswers;
import org.sibel.config.Settings;
import org.sibel.constants.RedisKeys;
import org.sibel.constants.ScoOperationType;
import org.sibel.constants.SensorType;
import org.sibel.di.TestModule;
import org.sibel.factories.InstantProvider;
import org.sibel.factories.PatientMonitorFactory;
import org.sibel.factories.UuidProvider;
import org.sibel.mdib.MdibAccessBuilder;
import org.sibel.mocks.KafkaProducerMock;
import org.sibel.models.payloads.internal.PatientPayload;
import org.sibel.producers.KafkaMessageProducer;
import org.sibel.repositories.PatientMonitorRepository;
import org.sibel.utils.CacheClient;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.common.access.MdibAccessObservable;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.message.*;
import org.somda.sdc.biceps.model.participant.AbstractContextState;
import org.somda.sdc.biceps.model.participant.PatientContextState;
import org.somda.sdc.glue.consumer.PrerequisitesException;
import org.somda.sdc.glue.consumer.SdcRemoteDevice;
import org.somda.sdc.glue.consumer.SdcRemoteDevicesConnector;
import org.somda.sdc.glue.consumer.SetServiceAccess;
import org.somda.sdc.glue.consumer.sco.ScoTransaction;

public abstract class BaseIntegrationTest {
    protected final Injector injector;

    protected final KafkaProducerMock kafkaProducerMock;
    protected final SdcRemoteDevice connectedSdcRemoteDeviceMock = mock();
    protected final MdibAccessObservable mdibAccessObservableMock = mock();
    protected final SetServiceAccess setServiceAccessMock = mock();
    protected final CacheClient cacheClientMock;
    protected final RedisCommands<String, String> redisMock;
    protected final Settings settings;

    protected PatientMonitor connectedPatientMonitor;
    protected MdibAccess connectedPmMdibAccess;

    public BaseIntegrationTest() {
        injector = Guice.createInjector(new TestModule());

        // Load mocks
        kafkaProducerMock = (KafkaProducerMock) injector.getInstance(KafkaMessageProducer.class);
        cacheClientMock = injector.getInstance(CacheClient.class);
        redisMock = injector.getInstance(Key.get(new TypeLiteral<>() {}));
        settings = injector.getInstance(Settings.class);

        // Init connected PM
        try {
            connectedPmMdibAccess = new MdibAccessBuilder().build();
        } catch (PreprocessingException e) {
            fail("Failed to initialize base MdibAccess", e);
        }

        var patientMonitorFactory = injector.getInstance(PatientMonitorFactory.class);
        connectedPatientMonitor = patientMonitorFactory.create(TestConstants.CONNECTED_PM_DISCOVERED_DEVICE, mock());
    }

    protected void configureDefaultMocks() {
        kafkaProducerMock.reset();
        configureUuidProviderMock();
        configureInstantProviderMock();
        configureSdcRemoteDeviceConnector();
        configureSdcRemoteDevice();
        connectDefaultPatientMonitor(TestConstants.CONNECTED_PATIENT);
        configureRedisMock(false);
        configureSetServiceAccessMock(true);
    }

    protected void setConnectedPmMdibAccess(MdibAccess mdibAccess) {
        connectedPmMdibAccess = mdibAccess;
    }

    protected void configureUuidProviderMock() {
        var uuidProviderMock = injector.getInstance(UuidProvider.class);
        reset(uuidProviderMock);
        when(uuidProviderMock.get()).thenAnswer(AdditionalAnswers.returnsElementsOf(TestConstants.UUID_LIST));
    }

    protected void configureInstantProviderMock() {
        var instantProviderMock = injector.getInstance(InstantProvider.class);
        reset(instantProviderMock);
        when(instantProviderMock.now()).thenReturn(TestConstants.NOW);
    }

    protected void configureSdcRemoteDeviceConnector() {
        var sdcRemoteDevicesConnectorMock = injector.getInstance(SdcRemoteDevicesConnector.class);
        reset(sdcRemoteDevicesConnectorMock);
        try {
            // TODO: WHAT ABOUT THE PARAMETERS?
            when(sdcRemoteDevicesConnectorMock.connect(any(), any()))
                    .thenAnswer((context) -> Futures.immediateFuture(connectedSdcRemoteDeviceMock));
        } catch (PrerequisitesException e) {
            fail("Failed to init SdcRemoteDevicesConnector class", e);
        }
        when(sdcRemoteDevicesConnectorMock.disconnect(anyString())).thenReturn(Futures.immediateFuture(null));
    }

    protected void configureSdcRemoteDevice() {
        reset(connectedSdcRemoteDeviceMock, mdibAccessObservableMock);
        when(connectedSdcRemoteDeviceMock.getMdibAccess()).thenAnswer((context) -> connectedPmMdibAccess);
        when(connectedSdcRemoteDeviceMock.getMdibAccessObservable()).thenReturn(mdibAccessObservableMock);
        when(connectedSdcRemoteDeviceMock.isRunning()).thenReturn(true);
        when(connectedSdcRemoteDeviceMock.getSetServiceAccess()).thenReturn(setServiceAccessMock);
    }

    protected void connectDefaultPatientMonitor(PatientPayload connectedPatient) {
        connectedPatientMonitor.forceConnect(
                connectedSdcRemoteDeviceMock, TestConstants.CONNECTED_PM_ID, connectedPatient);
        var repository = injector.getInstance(PatientMonitorRepository.class);
        repository.add(connectedPatientMonitor);
    }

    protected void configureRedisMock(boolean patientAlreadyInUse) {
        reset(cacheClientMock, redisMock);

        when(cacheClientMock.getRedisCommands()).thenAnswer((context) -> redisMock);

        when(redisMock.set(
                        eq(RedisKeys.getDeviceKey(TestConstants.CONNECTED_PM_EPR)),
                        eq(TestConstants.CONSUMER_ID),
                        any()))
                .thenReturn("OK");
        var sharedPatientIdKey =
                RedisKeys.getSharedPatientIdKey(TestConstants.CONNECTED_PATIENT.getPrimaryIdentifier());
        when(redisMock.set(eq(sharedPatientIdKey), eq(TestConstants.CONNECTED_PM_ID), any()))
                .thenReturn(patientAlreadyInUse ? null : "OK");
        when(redisMock.get(sharedPatientIdKey))
                .thenReturn(patientAlreadyInUse ? TestConstants.DISCONNECTED_PM_ID : TestConstants.CONNECTED_PM_ID);
    }

    protected void configureSetServiceAccessMock(boolean shouldSucceed) {
        reset(setServiceAccessMock);
        if (shouldSucceed) {
            var invocationInfo = new InvocationInfo();
            invocationInfo.setInvocationState(InvocationState.FIN);
            var setContextStateResponse = new SetContextStateResponse();
            setContextStateResponse.setInvocationInfo(invocationInfo);
            var reportPart = new OperationInvokedReport.ReportPart();
            reportPart.setInvocationInfo(invocationInfo);

            ScoTransaction<SetContextStateResponse> setPatientContextResponse = mock();
            when(setPatientContextResponse.getResponse()).thenReturn(setContextStateResponse);
            when(setPatientContextResponse.waitForFinalReport(any())).thenReturn(List.of(reportPart));
            when(setServiceAccessMock.invoke(any(), eq(SetContextStateResponse.class)))
                    .thenReturn(Futures.immediateFuture(setPatientContextResponse));
        } else {
            when(setServiceAccessMock.invoke(any(), eq(SetContextStateResponse.class)))
                    .thenReturn(Futures.immediateFailedFuture(new Exception("BOOM!")));
        }
    }

    protected void verifySetPatientScoNotCalled() {
        verify(setServiceAccessMock, never()).invoke(any(), any());
    }

    protected void verifySetPatientScoCalled(List<PatientContextState> patientContextStates) {
        var setPatientContext = new SetContextState();
        setPatientContext.setProposedContextState(patientContextStates.stream()
                .map(state -> (AbstractContextState) state)
                .toList());
        setPatientContext.setOperationHandleRef(getOperationHandle(SensorType.PM, ScoOperationType.SET_CONTEXT_STATE));

        verify(setServiceAccessMock).invoke(setPatientContext, SetContextStateResponse.class);
    }
}
