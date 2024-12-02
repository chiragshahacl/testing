package org.sibel.di;

import com.google.inject.AbstractModule;
import com.google.inject.util.Modules;
import org.somda.sdc.biceps.guice.DefaultBicepsConfigModule;
import org.somda.sdc.biceps.guice.DefaultBicepsModule;
import org.somda.sdc.common.guice.DefaultCommonConfigModule;
import org.somda.sdc.common.guice.DefaultCommonModule;
import org.somda.sdc.dpws.DpwsConfig;
import org.somda.sdc.dpws.guice.DefaultDpwsModule;
import org.somda.sdc.glue.guice.DefaultGlueConfigModule;
import org.somda.sdc.glue.guice.DefaultGlueModule;
import org.somda.sdc.glue.guice.GlueDpwsConfigModule;

public class SdcModule extends AbstractModule {
    private final boolean useTls;

    public SdcModule(boolean useTls) {
        this.useTls = useTls;
    }

    @Override
    protected void configure() {
        // Install SDC modules
        install(new DefaultCommonConfigModule());
        install(new DefaultGlueModule());
        install(new DefaultGlueConfigModule());
        install(new DefaultBicepsModule());
        install(new DefaultBicepsConfigModule());
        install(new DefaultCommonModule());
        // Override used to implement MDPWS
        install(Modules.override(new DefaultDpwsModule()).with(new CustomDpwsModule()));
        // Config module must override the existing modules
        install(Modules.override(new GlueDpwsConfigModule() {
                    @Override
                    protected void customConfigure() {
                        super.customConfigure();
                        bind(DpwsConfig.HTTPS_SUPPORT, Boolean.class, useTls);
                        bind(DpwsConfig.HTTP_SUPPORT, Boolean.class, !useTls);
                    }
                })
                .with(new ConfigModule()));
    }
}
