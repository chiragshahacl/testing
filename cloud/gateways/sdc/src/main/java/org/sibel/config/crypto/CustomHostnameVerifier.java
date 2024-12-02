package org.sibel.config.crypto;

import com.google.inject.Inject;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.SignatureException;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.util.Arrays;
import java.util.Objects;
import javax.net.ssl.HostnameVerifier;
import javax.net.ssl.SSLSession;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.somda.sdc.glue.GlueConstants;

public class CustomHostnameVerifier implements HostnameVerifier {
    private static final Logger LOG = LogManager.getLogger();

    private final X509Certificate intermediateCACert;

    @Inject
    public CustomHostnameVerifier(Settings settings) {
        intermediateCACert = loadCACertificate(settings.CRYPTO_CA_CERT_PATH());
    }

    public boolean verify(String hostname, SSLSession session) {
        try {
            var intermediateCaInChain = Arrays.stream(session.getPeerCertificates())
                    .anyMatch(certificate -> {
                        if (certificate instanceof X509Certificate) {
                            return signedByIntermediateCA((X509Certificate) certificate);
                        }
                        return false;
                    });

            if (intermediateCaInChain) {
                var x509certificate = (X509Certificate) session.getPeerCertificates()[0];
                var extendedKeyUsage = x509certificate.getExtendedKeyUsage();
                if (extendedKeyUsage != null && !extendedKeyUsage.isEmpty()) {
                    return extendedKeyUsage.stream()
                            .anyMatch(key -> Objects.equals(key, GlueConstants.OID_KEY_PURPOSE_SDC_SERVICE_PROVIDER));
                } else {
                    LOG.error("Connection rejected: No EKU in peer certificate");
                }
            } else {
                LOG.error("Connection rejected: Intermediate CA not in certificate chain");
            }

            return false;
        } catch (Exception e) {
            LOG.error("Connection rejected: Error while validating provider certificate: {}", e.getMessage(), e);
        }
        return false;
    }

    private X509Certificate loadCACertificate(String cryptoCaCertPath) {
        try (var inputStream = Files.newInputStream(Path.of(cryptoCaCertPath))) {
            var certFactory = CertificateFactory.getInstance("X.509");
            return (X509Certificate) certFactory.generateCertificate(inputStream);
        } catch (Exception e) {
            throw new RuntimeException("Error loading CA certificate: " + e.getMessage(), e);
        }
    }

    private boolean signedByIntermediateCA(X509Certificate cert) {
        if (intermediateCACert == null) {
            throw new IllegalStateException("Intermediate CA certificate was not loaded.");
        }

        var subjectMatches = intermediateCACert.getSubjectX500Principal().equals(cert.getIssuerX500Principal());
        if (subjectMatches) {
            try {
                cert.verify(intermediateCACert.getPublicKey());
                return true;
            } catch (CertificateException
                    | NoSuchAlgorithmException
                    | SignatureException
                    | InvalidKeyException
                    | NoSuchProviderException e) {
                LOG.warn("Client certificate does not match intermediate CA public key", e);
            }
        } else {
            LOG.warn("Client certificate does not match intermediate CA subject");
        }

        return false;
    }
}
