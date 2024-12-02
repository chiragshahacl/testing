package org.sibel.utils;

public class StringUtils {
    public static String trim(String value) {
        return value != null ? value.trim() : null;
    }

    public static String uppercase(String gender) {
        return gender != null ? gender.toUpperCase() : null;
    }
}
