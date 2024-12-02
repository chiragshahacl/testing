package org.sibel.apis.auth;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTCreationException;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import java.security.NoSuchAlgorithmException;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.sibel.config.Settings;
import org.sibel.emulator.metrics.AbstractMetricEmulator;
import org.sibel.factories.InstantProvider;

@Singleton
public class JWTAuthImpl implements JWTAuth {
    private static final Logger LOG = LogManager.getLogger(AbstractMetricEmulator.class);

    public static String AUDIENCE = "tucana";
    public static String ISSUER = "sdc";
    public static String USERNAME = "system";
    public static String TENANT_ID = "sibel";

    private RSAKeyProvider keyProvider;
    private Settings settings;
    private final InstantProvider instantProvider;
    private String jwtToken = null;
    private Instant tokenExpiration;

    @Inject
    public JWTAuthImpl(Settings settings, RSAKeyProvider keyProvider, InstantProvider instantProvider) {
        this.settings = settings;
        this.keyProvider = keyProvider;
        this.instantProvider = instantProvider;
    }

    @Override
    public boolean tokenHasExpired() {
        return this.instantProvider.now().isAfter(this.tokenExpiration);
    }

    @Override
    public String generateToken() {
        String token = "";
        try {
            RSAPublicKey publicKey = keyProvider.parsePublicKey(settings.JWT_PUBLIC_KEY());
            RSAPrivateKey privateKey = keyProvider.parsePrivateKey(settings.JWT_PRIVATE_KEY());
            Algorithm algorithm = Algorithm.RSA256(publicKey, privateKey);
            Instant expiration = this.instantProvider.now().plus(24, ChronoUnit.HOURS);
            this.tokenExpiration = expiration;
            token = JWT.create()
                    .withExpiresAt(expiration)
                    .withAudience(AUDIENCE)
                    .withIssuer(ISSUER)
                    .withClaim("username", USERNAME)
                    .withClaim("tenant_id", TENANT_ID)
                    .withClaim("user_id", USERNAME)
                    .sign(algorithm);
        } catch (JWTCreationException | NoSuchAlgorithmException | InvalidKeySpecException exception) {
            LOG.error("Could not generate JWT token", exception);
        }
        return token;
    }

    @Override
    public String getJwtToken() {
        if (jwtToken == null || tokenHasExpired()) {
            this.jwtToken = generateToken();
        }
        return this.jwtToken;
    }
}
