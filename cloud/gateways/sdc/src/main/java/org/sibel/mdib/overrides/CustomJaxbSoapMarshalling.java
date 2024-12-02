package org.sibel.mdib.overrides;

import com.google.common.util.concurrent.AbstractIdleService;
import com.google.inject.Inject;
import com.google.inject.name.Named;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.Reader;
import javax.xml.bind.JAXBElement;
import javax.xml.bind.JAXBException;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.somda.sdc.common.CommonConfig;
import org.somda.sdc.common.logging.InstanceLogger;
import org.somda.sdc.dpws.soap.SoapMarshalling;
import org.somda.sdc.dpws.soap.model.Envelope;
import org.somda.sdc.dpws.soap.model.ObjectFactory;

/**
 * Creates XML input and output streams from {@link Envelope} instances by using JAXB.
 */
public class CustomJaxbSoapMarshalling extends AbstractIdleService implements SoapMarshalling {
    private static final Logger LOG = LogManager.getLogger(org.somda.sdc.dpws.soap.JaxbSoapMarshalling.class);

    private final Logger instanceLogger;
    private final ObjectFactory soapFactory;
    private final CustomJaxbMarshalling jaxbMarshalling;

    @Inject
    public CustomJaxbSoapMarshalling(
            @Named(CommonConfig.INSTANCE_IDENTIFIER) String frameworkIdentifier,
            ObjectFactory soapFactory,
            CustomJaxbMarshalling jaxbMarshalling) {
        this.instanceLogger = InstanceLogger.wrapLogger(LOG, frameworkIdentifier);
        this.soapFactory = soapFactory;
        this.jaxbMarshalling = jaxbMarshalling;
    }

    @Override
    protected void startUp() throws Exception {
        instanceLogger.info("SOAP marshalling started");
    }

    @Override
    protected void shutDown() {
        instanceLogger.info("SOAP marshalling stopped");
    }

    /**
     * Takes a SOAP envelope and marshals it.
     *
     * @param envelope     the source envelope to marshal.
     * @param outputStream the destination of the marshalled data.
     * @throws JAXBException if marshalling fails.
     */
    @Override
    public void marshal(Envelope envelope, OutputStream outputStream) throws JAXBException {
        checkRunning();
        jaxbMarshalling.marshal(soapFactory.createEnvelope(envelope), outputStream);
    }

    private void checkRunning() {
        if (!isRunning()) {
            throw new RuntimeException("Try to marshal, but SOAP marshalling service is not running. "
                    + "Please check if the DPWS framework is up and running.");
        }
    }

    /**
     * Takes an input stream and unmarshals it.
     *
     * @param inputStream the input stream to unmarshal.
     * @return the unmarshalled SOAP envelope.
     * @throws JAXBException      if unmarshalling fails.
     * @throws ClassCastException in case unmarshalled data could not be cast to a JAXB element.
     */
    @Override
    @SuppressWarnings("unchecked")
    public Envelope unmarshal(InputStream inputStream) throws JAXBException, ClassCastException {
        checkRunning();
        var envelope = (JAXBElement<Envelope>) jaxbMarshalling.unmarshal(inputStream);
        return envelope.getValue();
    }

    /**
     * Takes a reader and unmarshals it.
     *
     * @param reader the input stream to unmarshal.
     * @return the unmarshalled SOAP envelope.
     * @throws JAXBException      if unmarshalling fails.
     * @throws ClassCastException in case unmarshalled data could not be cast to a JAXB element.
     */
    @Override
    @SuppressWarnings("unchecked")
    public Envelope unmarshal(Reader reader) throws JAXBException, ClassCastException {
        checkRunning();
        var envelope = (JAXBElement<Envelope>) jaxbMarshalling.unmarshal(reader);
        return envelope.getValue();
    }
}
