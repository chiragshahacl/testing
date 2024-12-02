package org.sibel.di;

import com.google.inject.AbstractModule;
import com.google.inject.Provides;
import com.google.inject.Scopes;
import com.google.inject.matcher.Matchers;
import com.google.inject.name.Named;
import com.google.inject.name.Names;
import java.util.List;
import java.util.Objects;
import java.util.stream.Stream;
import javax.net.ssl.HostnameVerifier;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.config.SettingsImpl;
import org.sibel.config.SettingsTypeListener;
import org.sibel.config.crypto.CustomCryptoSettings;
import org.sibel.config.crypto.CustomHostnameVerifier;
import org.somda.sdc.dpws.crypto.CryptoConfig;
import org.somda.sdc.dpws.crypto.CryptoSettings;

public class ConfigModule extends AbstractModule {
    private static final Logger LOG = LogManager.getLogger();

    @Override
    protected void configure() {
        bind(Settings.class).to(SettingsImpl.class).in(Scopes.SINGLETON);
        bindListener(Matchers.any(), new SettingsTypeListener());
        bind(HostnameVerifier.class)
                .annotatedWith(Names.named(CryptoConfig.CRYPTO_CLIENT_HOSTNAME_VERIFIER))
                .to(CustomHostnameVerifier.class);
    }

    @Provides
    @Named(CryptoConfig.CRYPTO_SETTINGS)
    public CryptoSettings createCustomCryptoSettings(Settings settings) {
        // certificates method
        var userKey = settings.CRYPTO_USER_KEY_PATH();
        var userCert = settings.CRYPTO_USER_CERT_PATH();
        var caCert = settings.CRYPTO_CA_CERT_PATH();
        var userKeyPassword = settings.CRYPTO_USER_KEY_PASSWORD();
        List<String> fingerprintBlacklist =
                settings.FINGERPRINT_BLACKLIST() != null ? settings.FINGERPRINT_BLACKLIST() : List.of();

        if (Stream.of(userKey, userCert, caCert, userKeyPassword).allMatch(Objects::nonNull)) {
            LOG.info("Using certificate files. userKey {} userCert {} caCert {}", userKey, userCert, caCert);
            return CustomCryptoSettings.fromKeyFile(fingerprintBlacklist, userKey, userCert, caCert, userKeyPassword);
        }
        return new CustomCryptoSettings(fingerprintBlacklist);
    }
}
