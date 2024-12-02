package org.sibel.apis.auth;

import java.security.NoSuchAlgorithmException;
import java.security.interfaces.RSAPrivateKey;
import java.security.interfaces.RSAPublicKey;
import java.security.spec.InvalidKeySpecException;

public interface RSAKeyProvider {
    RSAPrivateKey parsePrivateKey(String privateKeyString) throws NoSuchAlgorithmException, InvalidKeySpecException;

    RSAPublicKey parsePublicKey(String publicKeyString) throws NoSuchAlgorithmException, InvalidKeySpecException;
}
