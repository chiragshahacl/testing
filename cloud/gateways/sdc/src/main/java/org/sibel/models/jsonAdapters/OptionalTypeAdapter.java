package org.sibel.models.jsonAdapters;

import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;
import java.io.IOException;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.math.BigDecimal;
import java.util.Optional;

public class OptionalTypeAdapter<T> extends TypeAdapter<Optional<T>> {

    private boolean isOptionalOfBigDecimal(Optional<?> optional) {
        Type type = optional.getClass().getGenericSuperclass();

        if (type instanceof ParameterizedType parameterizedType) {
            Type[] typeArguments = parameterizedType.getActualTypeArguments();

            if (typeArguments.length == 1) {
                Type typeArgument = typeArguments[0];
                if (typeArgument instanceof Class<?> typeClass) {
                    return typeClass == BigDecimal.class;
                }
            }
        }
        return false;
    }

    private boolean isOptionalOfString(Optional<?> optional) {
        Type type = optional.getClass().getGenericSuperclass();

        if (type instanceof ParameterizedType parameterizedType) {
            Type[] typeArguments = parameterizedType.getActualTypeArguments();

            if (typeArguments.length == 1) {
                Type typeArgument = typeArguments[0];
                if (typeArgument instanceof Class<?> typeClass) {
                    return typeClass == String.class;
                }
            }
        }
        return false;
    }

    @Override
    public void write(JsonWriter out, Optional<T> optional) throws IOException {
        if (optional.isPresent() && this.isOptionalOfString(optional)) {
            out.value((String) optional.get());
        } else if (optional.isPresent() && this.isOptionalOfBigDecimal(optional)) {
            out.value((BigDecimal) optional.get());
        } else {
            out.nullValue();
        }
    }

    @Override
    public Optional<T> read(JsonReader in) throws IOException {
        // Implement your logic here to deserialize the Optional<T> object
        throw new UnsupportedOperationException("Deserialization of Optional not supported");
    }
}
