package org.sibel.factories;

import java.time.Instant;

public class InstantProviderImpl implements InstantProvider {
    @Override
    public Instant now() {
        return Instant.now();
    }
}
