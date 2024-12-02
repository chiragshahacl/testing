package org.sibel.factories;

import com.google.inject.assistedinject.Assisted;
import org.sibel.dataProcessors.*;
import org.somda.sdc.biceps.common.access.MdibAccess;
import org.somda.sdc.biceps.model.participant.*;

public interface ProcessorFactory {
    AlertChangeProcessor createAlertChangeProcessor(
            MdibAccess mdibAccess,
            AlertSignalState state,
            @Assisted("gatewayId") String gatewayId,
            @Assisted("gatewayModelNumber") String gatewayModelNumber,
            @Assisted("patientPrimaryIdentifier") String patientPrimaryIdentifier);

    ComponentStateChangeProcessor createComponentStateChangeProcessor(
            MdibAccess mdibAccess,
            AbstractDeviceComponentState state,
            @Assisted("gatewayId") String gatewayId,
            @Assisted("patientPrimaryIdentifier") String patientPrimaryIdentifier);

    MetricChangeProcessor createMetricChangeProcessor(
            MdibAccess mdibAccess, AbstractMetricState state, String patientPrimaryIdentifier);

    PatientContextChangeProcessor createPatientContextProcessor(PatientContextState context);

    VitalRangeProcessor createVitalRangeProcessor(MdibAccess mdibAccess, LimitAlertConditionState state);

    WaveformChangeProcessor createWaveformChangeProcessor(
            MdibAccess mdibAccess, RealTimeSampleArrayMetricState state, String patientPrimaryIdentifier);
}
