package org.sibel.apis.auth;

public interface JWTAuth {
    String generateToken();

    boolean tokenHasExpired();

    String getJwtToken();
}
