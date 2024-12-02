package org.sibel.config.crypto;

import java.security.MessageDigest;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.util.List;
import javax.net.ssl.X509TrustManager;
import javax.xml.bind.DatatypeConverter;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class BlacklistTrustManager implements X509TrustManager {
    private static final Logger LOG = LogManager.getLogger();

    private final List<String> fingerprintBlacklist;

    public BlacklistTrustManager(List<String> fingerprintBlacklist) {
        this.fingerprintBlacklist = fingerprintBlacklist;
    }

    @Override
    public void checkClientTrusted(X509Certificate[] x509Certificates, String authType) throws CertificateException {
        checkTrusted(x509Certificates);
    }

    @Override
    public void checkServerTrusted(X509Certificate[] x509Certificates, String authType) throws CertificateException {
        checkTrusted(x509Certificates);
    }

    private void checkTrusted(X509Certificate[] x509Certificates) throws CertificateException {
        // Get the first certificate in the chain (usually the server's certificate)
        var certificate = x509Certificates[0];

        try {
            var sha256Fingerprint = getFingerprint(certificate, "SHA-256");
            var sha1Fingerprint = getFingerprint(certificate, "SHA-1");
            var md5Fingerprint = getFingerprint(certificate, "MD5");

            if (fingerprintBlacklist.stream()
                    .anyMatch(fingerprint -> fingerprint.equals(sha256Fingerprint)
                            || fingerprint.equals(sha1Fingerprint)
                            || fingerprint.equals(md5Fingerprint))) {
                LOG.warn(
                        "Device using blacklisted fingerprint SHA-256: {}, SHA-1: {}, MD5: {}",
                        sha256Fingerprint,
                        sha1Fingerprint,
                        md5Fingerprint);
                throw new CertificateException("Certificate is blacklisted");
            }
        } catch (CertificateException e) {
            throw e;
        } catch (Exception e) {
            throw new CertificateException("Error checking certificate fingerprint", e);
        }
    }

    @Override
    public X509Certificate[] getAcceptedIssuers() {
        return new X509Certificate[0];
    }

    private String getFingerprint(X509Certificate cert, String hashAlgorithm) throws Exception {
        // Get the certificate in DER format
        var encoded = cert.getEncoded();

        // Compute the hash using the specified algorithm (SHA-256, SHA-1, MD5)
        var digest = MessageDigest.getInstance(hashAlgorithm).digest(encoded);

        // Convert the hash to a hexadecimal string
        return DatatypeConverter.printHexBinary(digest).toUpperCase();
    }
}
