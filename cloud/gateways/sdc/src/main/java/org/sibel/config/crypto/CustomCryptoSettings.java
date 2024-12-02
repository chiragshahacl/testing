package org.sibel.config.crypto;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.*;
import java.security.cert.Certificate;
import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import javax.annotation.Nullable;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;
import javax.net.ssl.TrustManagerFactory;
import org.apache.commons.lang3.ArrayUtils;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.bouncycastle.asn1.pkcs.PrivateKeyInfo;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import org.bouncycastle.openssl.PEMParser;
import org.bouncycastle.openssl.jcajce.JcaPEMKeyConverter;
import org.bouncycastle.openssl.jcajce.JceOpenSSLPKCS8DecryptorProviderBuilder;
import org.bouncycastle.operator.InputDecryptorProvider;
import org.bouncycastle.operator.OperatorCreationException;
import org.bouncycastle.pkcs.PKCS8EncryptedPrivateKeyInfo;
import org.bouncycastle.pkcs.PKCSException;
import org.somda.sdc.dpws.crypto.CachingCryptoSettings;

public class CustomCryptoSettings implements CachingCryptoSettings {
    private static final Logger LOG = LogManager.getLogger(CustomCryptoSettings.class);

    private static final String DEFAULT_KEYSTORE = "crypto/sdcparticipant.jks";
    private static final String DEFAULT_TRUSTSTORE = "crypto/root.jks";
    private static final String DEFAULT_KEYSTORE_PASSWORD = "whatever";
    private static final String DEFAULT_TRUSTSTORE_PASSWORD = "whatever";

    private @Nullable SSLContext cachedContext = null;

    private final List<String> fingerprintBlacklist;
    private byte[] keyStore = null;
    private byte[] trustStore = null;
    private String keyStorePassword = null;
    private String trustStorePassword = null;

    public CustomCryptoSettings(
            List<String> fingerprintBlacklist,
            byte[] keyStore,
            byte[] trustStore,
            String keyStorePassword,
            String trustStorePassword) {
        this.fingerprintBlacklist = fingerprintBlacklist;
        this.keyStore = keyStore;
        this.trustStore = trustStore;
        this.keyStorePassword = keyStorePassword;
        this.trustStorePassword = trustStorePassword;
    }

    public CustomCryptoSettings(List<String> fingerprintBlacklist) {
        this.fingerprintBlacklist = fingerprintBlacklist;
    }

    public static CustomCryptoSettings fromKeyStore(
            List<String> fingerprintBlacklist,
            String keyStorePath,
            String trustStorePath,
            String keyStorePassword,
            String trustStorePassword) {
        byte[] keyStoreFile;
        byte[] trustStoreFile;
        try {
            keyStoreFile = Files.readAllBytes(Path.of(keyStorePath));
            trustStoreFile = Files.readAllBytes(Path.of(trustStorePath));
        } catch (IOException e) {
            LOG.error("Specified store file could not be found", e);
            throw new RuntimeException("Specified store file could not be found", e);
        }

        return new CustomCryptoSettings(
                fingerprintBlacklist, keyStoreFile, trustStoreFile, keyStorePassword, trustStorePassword);
    }

    public static CustomCryptoSettings fromKeyFile(
            List<String> fingerprintBlacklist,
            String userKeyFilePath,
            String userCertFilePath,
            String caCertFilePath,
            String userKeyPassword) {
        Security.addProvider(new BouncyCastleProvider());

        byte[] userKeyFile;
        byte[] userCertFile;
        byte[] caCertFile;
        try {
            userKeyFile = Files.readAllBytes(Path.of(userKeyFilePath));
            userCertFile = Files.readAllBytes(Path.of(userCertFilePath));
            caCertFile = Files.readAllBytes(Path.of(caCertFilePath));
        } catch (IOException e) {
            var errorMessage =
                    "Specified certificate files could not be found. userKeyFilePath: %s userCertFilePath: %s caCertFilePath: %s."
                            .formatted(userKeyFilePath, userCertFilePath, caCertFilePath);
            LOG.error(errorMessage, e);
            throw new RuntimeException(errorMessage, e);
        }

        PrivateKey userKey;
        Certificate userCert;
        Certificate caCert;

        try {
            var cf = CertificateFactory.getInstance("X.509");

            // private key
            userKey = getPrivateKey(userKeyFile, userKeyPassword);

            // public key
            userCert = cf.generateCertificate(new ByteArrayInputStream(userCertFile));

            // ca cert
            caCert = cf.generateCertificate(new ByteArrayInputStream(caCertFile));
        } catch (CertificateException | IOException e) {
            var errorMessage =
                    "Specified certificate files could not be found. userKeyFilePath: %s userCertFilePath: %s caCertFilePath: %s."
                            .formatted(userKeyFilePath, userCertFilePath, caCertFilePath);
            LOG.error(errorMessage, e);
            throw new RuntimeException(errorMessage, e);
        }

        KeyStore keyStore;
        KeyStore trustStore;
        try {
            keyStore = KeyStore.getInstance(KeyStore.getDefaultType());
            keyStore.load(null);
            trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
            trustStore.load(null);
        } catch (CertificateException | NoSuchAlgorithmException | IOException | KeyStoreException e) {
            LOG.error("Error creating keystore instance", e);
            throw new RuntimeException("Error creating keystore instance", e);
        }

        try {
            keyStore.setKeyEntry("key", userKey, userKeyPassword.toCharArray(), new Certificate[] {userCert});
            trustStore.setCertificateEntry("ca", caCert);
        } catch (KeyStoreException e) {
            LOG.error("Error loading certificate into keystore instance", e);
            throw new RuntimeException("Error loading certificate into keystore instance", e);
        }

        var keyStoreOutputStream = new ByteArrayOutputStream();
        var trustStoreOutputStream = new ByteArrayOutputStream();

        try {
            keyStore.store(keyStoreOutputStream, userKeyPassword.toCharArray());
            trustStore.store(trustStoreOutputStream, userKeyPassword.toCharArray());
        } catch (KeyStoreException | IOException | NoSuchAlgorithmException | CertificateException e) {
            LOG.error("Error converting keystore to stream", e);
            throw new RuntimeException("Error converting keystore to stream", e);
        }

        return new CustomCryptoSettings(
                fingerprintBlacklist,
                keyStoreOutputStream.toByteArray(),
                trustStoreOutputStream.toByteArray(),
                userKeyPassword,
                userKeyPassword);
    }

    private static PrivateKey getPrivateKey(byte[] key, String password) throws IOException {

        PEMParser pp = new PEMParser(new BufferedReader(new InputStreamReader(new ByteArrayInputStream(key))));
        var pemKey = (PKCS8EncryptedPrivateKeyInfo) pp.readObject();
        pp.close();

        InputDecryptorProvider pkcs8Prov;
        try {
            pkcs8Prov = new JceOpenSSLPKCS8DecryptorProviderBuilder().build(password.toCharArray());
        } catch (OperatorCreationException e) {
            throw new IOException(e);
        }
        JcaPEMKeyConverter converter = new JcaPEMKeyConverter().setProvider(new BouncyCastleProvider());

        PrivateKeyInfo decrypted;
        try {
            decrypted = pemKey.decryptPrivateKeyInfo(pkcs8Prov);
        } catch (PKCSException e) {
            throw new IOException(e);
        }
        return converter.getPrivateKey(decrypted);
    }

    @Override
    public Optional<InputStream> getKeyStoreStream() {
        if (keyStore != null) {
            return Optional.of(new ByteArrayInputStream(keyStore));
        }
        return Optional.ofNullable(getClass().getClassLoader().getResourceAsStream(DEFAULT_KEYSTORE));
    }

    @Override
    public String getKeyStorePassword() {
        return Objects.requireNonNullElse(this.keyStorePassword, DEFAULT_KEYSTORE_PASSWORD);
    }

    @Override
    public Optional<InputStream> getTrustStoreStream() {
        if (trustStore != null) {
            return Optional.of(new ByteArrayInputStream(trustStore));
        }
        return Optional.ofNullable(getClass().getClassLoader().getResourceAsStream(DEFAULT_TRUSTSTORE));
    }

    @Override
    public String getTrustStorePassword() {
        return Objects.requireNonNullElse(trustStorePassword, DEFAULT_TRUSTSTORE_PASSWORD);
    }

    @Override
    public synchronized Optional<SSLContext> getSslContext() {
        try {
            cachedContext = SSLContext.getInstance("TLS");

            // Load the client keystore (which contains client certificates and keys)
            KeyStore keyStoreObject = KeyStore.getInstance("JKS");
            keyStoreObject.load(new ByteArrayInputStream(keyStore), keyStorePassword.toCharArray());

            // Create a KeyManagerFactory with the KeyStore
            KeyManagerFactory keyManagerFactory =
                    KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
            keyManagerFactory.init(keyStoreObject, keyStorePassword.toCharArray()); // Initialize with the key password

            // Load the truststore (which contains the certificates you trust)
            KeyStore trustStoreObj = KeyStore.getInstance("JKS");
            trustStoreObj.load(new ByteArrayInputStream(trustStore), trustStorePassword.toCharArray());

            // Create a TrustManagerFactory with the truststore
            TrustManagerFactory trustManagerFactory =
                    TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
            trustManagerFactory.init(trustStoreObj);

            // Add blacklist trust manager
            var trustManagers =
                    ArrayUtils.addAll(trustManagerFactory.getTrustManagers(), ArrayUtils.toArray((TrustManager)
                            new BlacklistTrustManager(fingerprintBlacklist)));

            // Re-init the SSL context with the custom trust manager that we want
            cachedContext.init(keyManagerFactory.getKeyManagers(), trustManagers, new SecureRandom());
        } catch (IOException
                | NoSuchAlgorithmException
                | CertificateException
                | UnrecoverableKeyException
                | KeyStoreException
                | KeyManagementException e) {
            // TODO: IMPROVE EXCEPTIONS
            throw new RuntimeException(e);
        }

        return Optional.ofNullable(cachedContext);
    }

    @Override
    public synchronized void setSslContext(final SSLContext sslContext) {
        cachedContext = sslContext;
    }
}
