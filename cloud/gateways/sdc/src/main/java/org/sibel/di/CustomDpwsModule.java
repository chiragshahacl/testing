package org.sibel.di;

import com.google.inject.AbstractModule;
import org.sibel.mdib.overrides.CustomJaxbMarshalling;
import org.sibel.mdib.overrides.CustomJaxbSoapMarshalling;
import org.sibel.mdib.overrides.CustomJaxbWsdlMarshalling;
import org.somda.sdc.dpws.soap.SoapMarshalling;
import org.somda.sdc.dpws.wsdl.WsdlMarshalling;

public class CustomDpwsModule extends AbstractModule {
    @Override
    protected void configure() {
        bind(CustomJaxbMarshalling.class).asEagerSingleton();
        bind(SoapMarshalling.class).to(CustomJaxbSoapMarshalling.class).asEagerSingleton();
        bind(WsdlMarshalling.class).to(CustomJaxbWsdlMarshalling.class).asEagerSingleton();
    }
}
