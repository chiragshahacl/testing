package org.sibel;

import static org.sibel.mdib.MdibDescriptorFactory.createPatientContextDescriptor;
import static org.sibel.mdib.MdibStateFactory.*;

import com.google.common.util.concurrent.AbstractIdleService;
import com.google.inject.Injector;
import java.io.IOException;
import java.math.BigDecimal;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.constants.*;
import org.sibel.emulator.AnneChestEmulator;
import org.sibel.emulator.AnneLimbEmulator;
import org.sibel.emulator.DeviceEmulator;
import org.sibel.emulator.gui.NoGui;
import org.sibel.emulator.gui.PatientInfo;
import org.sibel.emulator.gui.ProviderGui;
import org.sibel.emulator.gui.ProviderGuiImpl;
import org.sibel.emulator.receivers.SetPatientContextReceiver;
import org.sibel.mdib.MdibAccessBuilder;
import org.sibel.mdib.mdpws.SelectorType;
import org.sibel.mdib.overrides.CustomJaxbMarshalling;
import org.sibel.utils.ProviderUtil;
import org.somda.sdc.biceps.common.MdibDescriptionModifications;
import org.somda.sdc.biceps.common.MdibStateModifications;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.model.participant.AlertActivation;
import org.somda.sdc.biceps.model.participant.AlertSignalPresence;
import org.somda.sdc.biceps.model.participant.BatteryState;
import org.somda.sdc.biceps.model.participant.ContextAssociation;
import org.somda.sdc.biceps.provider.access.LocalMdibAccess;
import org.somda.sdc.dpws.DpwsFramework;
import org.somda.sdc.dpws.DpwsUtil;
import org.somda.sdc.dpws.device.DeviceSettings;
import org.somda.sdc.dpws.soap.wsaddressing.WsAddressingUtil;
import org.somda.sdc.dpws.soap.wsaddressing.model.EndpointReferenceType;
import org.somda.sdc.glue.provider.SdcDevice;
import org.somda.sdc.glue.provider.factory.SdcDeviceFactory;
import org.somda.sdc.glue.provider.plugin.SdcRequiredTypesAndScopes;

public class Provider extends AbstractIdleService {
    private static final Logger LOG = LogManager.getLogger(Provider.class);

    private final Injector injector;
    private final LocalMdibAccess mdibAccess;
    private final DpwsFramework dpwsFramework;
    private final SdcDevice sdcDevice;
    private AnneChestEmulator.EcgMode ecgMode;
    private String serialNumber;
    private ProviderGui gui;
    private List<DeviceEmulator> emulators = null;
    private Lock emulatorLock = new ReentrantLock();

    /**
     * Create an instance of an SDC Provider.
     *
     * @param providerUtil options and configured injector
     * @throws SocketException      thrown if network adapter cannot be set up
     * @throws UnknownHostException if provided address cannot be resolved to an adapter
     */
    public Provider(ProviderUtil providerUtil) throws SocketException, UnknownHostException, PreprocessingException {
        injector = providerUtil.getInjector();

        serialNumber = providerUtil.getSerialNumber();
        if (serialNumber == null || serialNumber.isEmpty()) {
            serialNumber = "9999-9999-9999-9999";
        }

        var patientId = providerUtil.getPatientId();
        if (patientId == null || patientId.isEmpty()) {
            patientId = "fake_patient_%s".formatted(UUID.randomUUID());
        }

        var ecgModeText = providerUtil.getEgcMode();
        if (Objects.equals(ecgModeText, "sin")) {
            ecgMode = AnneChestEmulator.EcgMode.SINUSOIDAL;
        } else {
            ecgMode = AnneChestEmulator.EcgMode.DEMO;
        }

        NetworkInterface networkInterface;
        if (providerUtil.getIface() != null && !providerUtil.getIface().isEmpty()) {
            LOG.info("Starting with interface {}", providerUtil.getIface());
            networkInterface = NetworkInterface.getByName(providerUtil.getIface());
        } else {
            if (providerUtil.getAddress() != null && !providerUtil.getAddress().isBlank()) {
                // bind to adapter matching ip
                LOG.info("Starting with address {}", providerUtil.getAddress());
                networkInterface = NetworkInterface.getByInetAddress(InetAddress.getByName(providerUtil.getAddress()));
            } else {
                // find loopback interface for fallback
                networkInterface = NetworkInterface.getByInetAddress(InetAddress.getLoopbackAddress());
                LOG.info("Starting with fallback default adapter {}", networkInterface);
            }
        }
        if (networkInterface == null) {
            throw new RuntimeException("No network interface");
        }
        dpwsFramework = injector.getInstance(DpwsFramework.class);
        dpwsFramework.setNetworkInterface(networkInterface);

        var anneChestId = UUID.randomUUID().toString();
        var anneLimbId = UUID.randomUUID().toString();

        // SafetyReq XPath for versioning attribute
        // TODO: SET THIS CORRECTLY
        var scoSafetyReqDefinition = new SelectorType();
        scoSafetyReqDefinition.setId("some random id"); // Should this ID be something ?
        scoSafetyReqDefinition.setValue(
                "//pm:MdDescription/pm:Mds/pm:Vmd[@Handle=\"sibel.anneone.annechest\"]/pm:Sco/pm:ScoDescriptor/@DescriptorVersion");

        // Init MDIB access
        var settings = injector.getInstance(Settings.class);
        mdibAccess = new MdibAccessBuilder(injector)
                .addPatient(
                        patientId,
                        List.of(settings.CENTRAL_HUB_VALIDATOR_ID(), settings.PATIENT_MONITOR_VALIDATOR_ID()))
                .addBattery(SensorType.PM, serialNumber, BigDecimal.valueOf(89), BatteryState.ChargeStatus.DIS_CH_B)
                .addBattery(
                        SensorType.ANNE_CHEST, anneChestId, BigDecimal.valueOf(75), BatteryState.ChargeStatus.DIS_CH_B)
                .addBattery(
                        SensorType.ANNE_LIMB, anneLimbId, BigDecimal.valueOf(75), BatteryState.ChargeStatus.DIS_CH_B)
                .addDevice(SensorType.ANNE_CHEST, anneChestId)
                .addDevice(SensorType.ANNE_LIMB, anneLimbId)
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.VITALS)
                .addMetricChannel(SensorType.ANNE_CHEST, MetricChannel.DEVICE)
                .addMetricChannel(SensorType.ANNE_LIMB, MetricChannel.VITALS)
                .addMetricChannel(SensorType.ANNE_LIMB, MetricChannel.DEVICE)
                .addRealTimeMetric(
                        SensorType.ANNE_CHEST,
                        Metric.ECG_WAVEFORM,
                        List.of(),
                        Duration.ofMillis(100),
                        Duration.ofMillis(100),
                        Instant.now())
                .addRealTimeMetric(
                        SensorType.ANNE_CHEST,
                        Metric.RR_WAVEFORM,
                        List.of(),
                        Duration.ofMillis(100),
                        Duration.ofMillis(100),
                        Instant.now())
                .addRealTimeMetric(
                        SensorType.ANNE_LIMB,
                        Metric.PLETH_WAVEFORM,
                        List.of(),
                        Duration.ofMillis(100),
                        Duration.ofMillis(100),
                        Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.HR, BigDecimal.valueOf(97), Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.CHEST_TEMP, BigDecimal.valueOf(97), Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.FALLS, BigDecimal.valueOf(0), Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.BODY_POSITION, "UPRIGHT", Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.BODY_ANGLE_UPRIGHT, BigDecimal.valueOf(0), Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.RR_METRIC, BigDecimal.valueOf(15), Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.DEVICE_SIGNAL, BigDecimal.valueOf(0), Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.DEVICE_LEAD, "true", Instant.now())
                .addMetric(SensorType.ANNE_CHEST, Metric.DEVICE_MODULE, "true", Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.SPO2, BigDecimal.valueOf(97), Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.PR, BigDecimal.valueOf(97), Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.PI, BigDecimal.valueOf(4.5), Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.LIMB_TEMP, BigDecimal.valueOf(97), Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.DEVICE_SIGNAL, BigDecimal.valueOf(0), Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.DEVICE_LEAD, "true", Instant.now())
                .addMetric(SensorType.ANNE_LIMB, Metric.DEVICE_MODULE, "true", Instant.now())
                .addAlertSystem(SensorType.PM)
                .addAlert(PhysiologicalAlert.HR_ME__VIS, false)
                .addAlert(PhysiologicalAlert.HR_ME__AUD, false)
                .addAlert(PhysiologicalAlert.RR_ME__VIS, false)
                .addAlertSystem(SensorType.ANNE_CHEST)
                .addAlertSystem(SensorType.ANNE_LIMB)
                .addAlert(SensorType.ANNE_CHEST, TechnicalAlert.LEAD_OFF, false)
                .addAlert(SensorType.ANNE_LIMB, TechnicalAlert.LEAD_OFF, false)
                .addSco(SensorType.PM)
                .addScoOperation(SensorType.PM, ScoOperationType.SET_CONTEXT_STATE, List.of(scoSafetyReqDefinition))
                .build();

        initGui(providerUtil, patientId);

        if (!providerUtil.isGuiEnabled()) {
            LOG.info("GUI disabled, starting vitals emulation automatically.");
            startSensorEmulation();
        }

        var epr = providerUtil.getEpr();
        if (epr == null) {
            epr = "urn:uuid:" + UUID.randomUUID();
            LOG.info("No epr address provided, generated random epr {}", epr);
        }

        String finalEpr = epr;
        var setPatientContextReceiver = new SetPatientContextReceiver(gui, settings);
        sdcDevice = injector.getInstance(SdcDeviceFactory.class)
                .createSdcDevice(
                        new DeviceSettings() {
                            @Override
                            public EndpointReferenceType getEndpointReference() {
                                return injector.getInstance(WsAddressingUtil.class)
                                        .createEprWithAddress(finalEpr);
                            }

                            @Override
                            public NetworkInterface getNetworkInterface() {
                                return networkInterface;
                            }
                        },
                        mdibAccess,
                        List.of(setPatientContextReceiver),
                        Collections.singleton(injector.getInstance(SdcRequiredTypesAndScopes.class)));
    }

    private void initGui(ProviderUtil providerUtil, String patientId) {
        var settings = injector.getInstance(Settings.class);
        if (providerUtil.isGuiEnabled()) {
            gui = new ProviderGuiImpl();
        } else {
            gui = new NoGui();
        }
        gui.setAudioChangeListener(this::setAudio);
        gui.setPatientChangeListener((patientInfo) -> {
            try {
                var modifications = MdibDescriptionModifications.create();
                var validators = new ArrayList<String>();
                if (patientInfo.validatedByCms()) {
                    validators.add(settings.CENTRAL_HUB_VALIDATOR_ID());
                }
                if (patientInfo.validatedByPm()) {
                    validators.add(settings.PATIENT_MONITOR_VALIDATOR_ID());
                }
                var patientContextState = createPatientContextState(
                        patientInfo.id(),
                        patientInfo.givenName(),
                        patientInfo.familyName(),
                        patientInfo.birthDate(),
                        patientInfo.gender(),
                        patientInfo.association(),
                        validators);
                modifications.update(createPatientContextDescriptor(), patientContextState);
                mdibAccess.writeDescription(modifications);

                LOG.info("Patient changed.");
                gui.setPatientInfo(patientInfo);
            } catch (Exception e) {
                LOG.error("Failed to set patient info", e);
            }
        });
        gui.setEmulationChangeListener(running -> {
            if (running) {
                startSensorEmulation();
            } else {
                stopSensorEmulation();
            }
        });
        gui.setPhysiologicalAlertChangeListener(this::setPhysiologicalAlerts);
        gui.setTechnicalAlertChangeListener(this::setTechnicalAlerts);
        gui.setBatteryChangeListener(this::setBattery);
        gui.setBodyAngleChangeListener(this::setBodyAngle);
        gui.setPatientInfo(new PatientInfo(patientId, null, null, null, null, ContextAssociation.ASSOC, true, true));
    }

    private void startSensorEmulation() {
        emulatorLock.lock();
        try {
            if (emulators == null) {
                emulators = List.of(new AnneChestEmulator(mdibAccess, ecgMode), new AnneLimbEmulator(mdibAccess));
                emulators.forEach(DeviceEmulator::start);
            } else {
                LOG.info("Emulation already started.");
            }
        } finally {
            emulatorLock.unlock();
        }
    }

    private void stopSensorEmulation() {
        emulatorLock.lock();
        try {
            if (emulators != null) {
                emulators.forEach(DeviceEmulator::stop);
                emulators = null;
            } else {
                LOG.info("Emulation already stopped.");
            }
        } finally {
            emulatorLock.unlock();
        }
    }

    @Override
    protected void startUp() {
        // Init custom marshalling service needed to run MDPWS
        var customMarshallingService = injector.getInstance(CustomJaxbMarshalling.class);
        customMarshallingService.startAsync().awaitRunning();

        DpwsUtil dpwsUtil = injector.getInstance(DpwsUtil.class);

        sdcDevice
                .getHostingServiceAccess()
                .setThisDevice(dpwsUtil.createDeviceBuilder()
                        .setFriendlyName(dpwsUtil.createLocalizedStrings()
                                .add("en", "Provider Example Unit")
                                .get())
                        .setFirmwareVersion("v1.2.3")
                        .setSerialNumber(serialNumber)
                        .get());

        sdcDevice
                .getHostingServiceAccess()
                .setThisModel(dpwsUtil.createModelBuilder()
                        .setManufacturer(dpwsUtil.createLocalizedStrings()
                                .add("en", "Provider Example Inc.")
                                .add("de", "Beispiel Provider AG")
                                .add("cn", "范例公司")
                                .get())
                        .setManufacturerUrl("http://www.example.com")
                        .setModelName(
                                dpwsUtil.createLocalizedStrings().add("PEU").get())
                        .setModelNumber("54-32-1")
                        .setPresentationUrl("http://www.example.com")
                        .get());

        dpwsFramework.startAsync().awaitRunning();
        sdcDevice.startAsync().awaitRunning();

        LOG.info("Provider started with S/N: {}", serialNumber);
    }

    @Override
    protected void shutDown() {
        stopSensorEmulation();
        sdcDevice.stopAsync().awaitTerminated();
        dpwsFramework.stopAsync().awaitTerminated();
    }

    private void setAudio(AlertActivation audioActivation) {
        var modifications = MdibStateModifications.create(MdibStateModifications.Type.ALERT);
        modifications.add(createAlertSystemState(SensorType.PM, audioActivation));
        try {
            mdibAccess.writeStates(modifications);
        } catch (PreprocessingException e) {
            LOG.error("Error updating audio settings", e);
        }
    }

    private void setTechnicalAlerts(SensorType device, TechnicalAlert alert, AlertSignalPresence presence) {
        var modifications = MdibStateModifications.create(MdibStateModifications.Type.ALERT);
        modifications.add(createAlertState(
                device, alert, presence == AlertSignalPresence.ON, presence == AlertSignalPresence.LATCH));
        modifications.add(createAlertConditionState(device, alert, presence == AlertSignalPresence.ON, Instant.now()));
        try {
            mdibAccess.writeStates(modifications);
        } catch (PreprocessingException e) {
            LOG.error("Error updating audio settings", e);
        }
    }

    private void setBattery(int value, BatteryState.ChargeStatus chargeStatus) {
        var modifications = MdibStateModifications.create(MdibStateModifications.Type.COMPONENT);
        modifications.add(
                createBatteryState(SensorType.ANNE_CHEST, BigDecimal.valueOf((float) value / 100.0), chargeStatus));
        try {
            mdibAccess.writeStates(modifications);
        } catch (PreprocessingException e) {
            LOG.error("Error updating audio settings", e);
        }
    }

    private void setBodyAngle(int angle, String position) {
        var modifications = MdibStateModifications.create(MdibStateModifications.Type.METRIC);
        modifications.add(createNumericMetricState(
                SensorType.ANNE_CHEST, Metric.BODY_ANGLE_UPRIGHT, BigDecimal.valueOf(angle), Instant.now()));
        modifications.add(
                createStringMetricState(SensorType.ANNE_CHEST, Metric.BODY_POSITION, position, Instant.now()));
        try {
            mdibAccess.writeStates(modifications);
        } catch (PreprocessingException e) {
            LOG.error("Error updating body angle", e);
        }
    }

    private void setPhysiologicalAlerts(List<PhysiologicalAlert> alerts, AlertSignalPresence presence) {
        var modifications = MdibStateModifications.create(MdibStateModifications.Type.ALERT);
        for (PhysiologicalAlert alert : alerts) {
            modifications.add(
                    createAlertState(alert, presence == AlertSignalPresence.ON, presence == AlertSignalPresence.LATCH));
            modifications.add(createAlertConditionState(alert, Instant.now(), presence == AlertSignalPresence.ON));
        }
        try {
            mdibAccess.writeStates(modifications);
        } catch (PreprocessingException e) {
            LOG.error("Error updating audio settings", e);
        }
    }

    public static void main(String[] args) throws IOException, PreprocessingException {
        var util = new ProviderUtil(args);

        Provider provider = new Provider(util);

        provider.startAsync().awaitRunning();

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            provider.stopAsync().awaitTerminated();
            LOG.info("Provider stopped.");
        }));

        // Open GUI to show the current patient
        provider.gui.open("Provider %s".formatted(provider.serialNumber));
    }
}
