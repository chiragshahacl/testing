package org.sibel.factories;

import java.util.UUID;

public class UuidProviderImpl implements UuidProvider {
    @Override
    public String get() {
        return UUID.randomUUID().toString();
    }
}
