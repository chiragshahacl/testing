package org.sibel.apis.auth;

import java.security.KeyFactory;
import java.security.NoSuchAlgorithmException;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;
import java.security.spec.PKCS8EncodedKeySpec;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import javax.inject.Singleton;

@Singleton
public class RSAKeyProviderImpl implements RSAKeyProvider {

    @Override
    public RSAPrivateKey parsePrivateKey(String privateKeyString)
            throws NoSuchAlgorithmException, InvalidKeySpecException {
        // Remove header, footer, and newlines from the key string
        privateKeyString = privateKeyString
                .replaceAll("^-----BEGIN.*-----", "")
                .replaceAll("-----END.*-----$", "")
                .replaceAll("\\s+", "");

        // Decode Base64 encoded string
        byte[] privateKeyBytes = Base64.getDecoder().decode(privateKeyString);

        // Generate private key
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        PKCS8EncodedKeySpec privateKeySpec = new PKCS8EncodedKeySpec(privateKeyBytes);
        return (RSAPrivateKey) keyFactory.generatePrivate(privateKeySpec);
    }

    @Override
    public RSAPublicKey parsePublicKey(String publicKeyString)
            throws NoSuchAlgorithmException, InvalidKeySpecException {
        // Remove header, footer, and newlines from the key string
        publicKeyString = publicKeyString
                .replaceAll("^-----BEGIN.*-----", "")
                .replaceAll("-----END.*-----$", "")
                .replaceAll("\\s+", "");

        // Decode Base64 encoded string
        byte[] publicKeyBytes = Base64.getDecoder().decode(publicKeyString);

        // Generate public key
        KeyFactory keyFactory = KeyFactory.getInstance("RSA");
        X509EncodedKeySpec publicKeySpec = new X509EncodedKeySpec(publicKeyBytes);
        return (RSAPublicKey) keyFactory.generatePublic(publicKeySpec);
    }
}
