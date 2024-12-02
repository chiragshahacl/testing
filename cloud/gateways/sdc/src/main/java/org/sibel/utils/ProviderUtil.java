package org.sibel.utils;

import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.core.config.Configurator;

/**
 * This class provides the configuration used for the consumer instance.
 * <p>
 * Overwriting configuration steps allows customizing the behavior of the framework through
 * injection.
 */
public class ProviderUtil extends BaseUtil {
    private static final String OPT_SERIAL_NUMBER = "sn";
    private static final String OPT_ECG_MODE = "ecgmode";
    private static final String OPT_PATIENT_ID = "patient";
    private static final String OPT_GUI_ENABLED = "gui";

    public ProviderUtil(String[] args) {
        super(args);

        Level logLevel = Level.getLevel(Level.DEBUG.name());
        Configurator.reconfigure(localLoggerConfig(logLevel));
    }

    @Override
    protected Options configureOptions() {
        var options = super.configureOptions();

        var serialNumberOption = new Option("s", OPT_SERIAL_NUMBER, true, "serial number of the emulated PM");
        serialNumberOption.setRequired(false);
        options.addOption(serialNumberOption);

        var ecgModeOption = new Option(null, OPT_ECG_MODE, true, "Emulation mode for ECG waveform");
        ecgModeOption.setRequired(false);
        options.addOption(ecgModeOption);

        var patientOption = new Option(null, OPT_PATIENT_ID, true, "Patient id to be set to the PM");
        patientOption.setRequired(false);
        options.addOption(patientOption);

        var guiOption =
                new Option(null, OPT_GUI_ENABLED, false, "Displays the GUI to show the current provider status");
        guiOption.setRequired(false);
        options.addOption(guiOption);

        return options;
    }

    public String getSerialNumber() {
        return getParsedArgs().getOptionValue(OPT_SERIAL_NUMBER);
    }

    public String getEgcMode() {
        return getParsedArgs().getOptionValue(OPT_ECG_MODE);
    }

    public String getPatientId() {
        return getParsedArgs().getOptionValue(OPT_PATIENT_ID);
    }

    public boolean isGuiEnabled() {
        return getParsedArgs().hasOption(OPT_GUI_ENABLED);
    }
}
