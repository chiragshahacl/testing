package org.sibel.mdib;

import static org.junit.jupiter.api.Assertions.*;

import com.google.inject.Guice;
import com.google.inject.util.Modules;
import java.math.BigDecimal;
import java.util.List;
import javax.xml.bind.JAXBException;
import org.junit.jupiter.api.Test;
import org.sibel.constants.ProductionSpecCodes;
import org.sibel.di.CustomDpwsModule;
import org.somda.sdc.biceps.common.MdibDescriptionModifications;
import org.somda.sdc.biceps.common.storage.PreprocessingException;
import org.somda.sdc.biceps.guice.DefaultBicepsConfigModule;
import org.somda.sdc.biceps.guice.DefaultBicepsModule;
import org.somda.sdc.biceps.model.participant.*;
import org.somda.sdc.biceps.provider.access.factory.LocalMdibAccessFactory;
import org.somda.sdc.common.guice.DefaultCommonConfigModule;
import org.somda.sdc.common.guice.DefaultCommonModule;
import org.somda.sdc.dpws.guice.DefaultDpwsModule;
import org.somda.sdc.glue.guice.DefaultGlueConfigModule;
import org.somda.sdc.glue.guice.DefaultGlueModule;
import org.somda.sdc.glue.guice.GlueDpwsConfigModule;

public class TestMdibCreate {

    @Test
    void testInsertMdib() throws PreprocessingException, JAXBException {
        var injector = Guice.createInjector(
                new DefaultCommonConfigModule(),
                new DefaultGlueModule(),
                new DefaultGlueConfigModule(),
                new DefaultBicepsModule(),
                new DefaultBicepsConfigModule(),
                new DefaultCommonModule(),
                // Override used to implement MDPWS
                Modules.override(new DefaultDpwsModule()).with(new CustomDpwsModule()),
                new GlueDpwsConfigModule());

        var descModification = MdibDescriptionModifications.create();

        var parentHandle = "sibel.anneone";

        var pmDescriptor = new MdsDescriptor();
        pmDescriptor.setHandle(parentHandle);
        var pmState = new MdsState();
        pmState.setDescriptorHandle(pmDescriptor.getHandle());
        descModification.insert(new MdibDescriptionModifications.Entry(pmDescriptor, pmState));

        var batteryHandle = "sibel.anneone.battery.pm";

        var batteryCodedValue = new CodedValue();
        batteryCodedValue.setCode("145003");
        var measurementUnitCodedValue = new CodedValue();
        measurementUnitCodedValue.setCode("262688");

        var productSpecificationCodedValue = new CodedValue();
        productSpecificationCodedValue.setSymbolicCodeName(ProductionSpecCodes.DEVICE_PRIMARY_IDENTIFIER);
        var productionSpecification = new AbstractDeviceComponentDescriptor.ProductionSpecification();
        productionSpecification.setSpecType(productSpecificationCodedValue);
        productionSpecification.setProductionSpec("PM-0001"); // PM serial

        var batteryDescriptor = new BatteryDescriptor();
        batteryDescriptor.setType(batteryCodedValue);
        batteryDescriptor.setHandle(batteryHandle);
        batteryDescriptor.setProductionSpecification(List.of(productionSpecification));

        var capacityRemaining = new Measurement();
        capacityRemaining.setMeasuredValue(BigDecimal.valueOf(50));
        capacityRemaining.setMeasurementUnit(measurementUnitCodedValue);
        var batteryState = new BatteryState();
        batteryState.setCapacityRemaining(capacityRemaining);
        batteryState.setDescriptorHandle(batteryHandle);

        var entry = new MdibDescriptionModifications.Entry(batteryDescriptor, batteryState, parentHandle);

        descModification.insert(entry);

        // Insert data
        var mdibAccess = injector.getInstance(LocalMdibAccessFactory.class).createLocalMdibAccess();
        mdibAccess.writeDescription(descModification);

        // Read data
        var readBatteryDescriptor = mdibAccess.getDescriptor(batteryHandle);
        assertEquals(readBatteryDescriptor.get().getHandle(), batteryDescriptor.getHandle());

        var readEntity = mdibAccess.getEntity(batteryHandle);
        var readDeviceDescriptor = readEntity.get().getDescriptor(AbstractDeviceComponentDescriptor.class);
        assertEquals(
                "PM-0001",
                readDeviceDescriptor.get().getProductionSpecification().get(0).getProductionSpec());
    }
}
