package org.sibel.factories;

import org.sibel.tasks.ConsumerReportProcessor;

public interface ConsumerReportProcessorFactory {
    ConsumerReportProcessor create(String patientMonitorId);
}
