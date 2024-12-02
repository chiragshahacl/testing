package org.sibel.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.sibel.exceptions.SettingsException;

public class TestSettingsMemberInjector {
    public class TestSetting {
        @SettingValue(variableName = "STRING_VALUE", configurationName = "value.string")
        String STRING_VALUE;

        @SettingValue(variableName = "NOT_REQUIRED_VALUE", configurationName = "value.notRequired", required = false)
        String NOT_REQUIRED_VALUE;

        @SettingValue(variableName = "DEFAULT_VALUE", configurationName = "value.default", defaultValue = "DEFAULT")
        String DEFAULT_VALUE;

        @SettingValue(variableName = "BOOLEAN_VALUE", configurationName = "value.boolean")
        boolean BOOLEAN_VALUE;

        @SettingValue(variableName = "INTEGER_VALUE", configurationName = "value.integer")
        int INTEGER_VALUE;

        @SettingValue(
                variableName = "CUSTOM_STRING_VALUE",
                configurationName = "value.customString",
                parserMethod = "customStringValueParser")
        String CUSTOM_STRING_VALUE;

        @SettingValue(
                variableName = "CUSTOM_VALUE_TYPE",
                configurationName = "value.customType",
                parserMethod = "customValueParser")
        List<String> CUSTOM_VALUE_TYPE;

        public static String customStringValueParser(String value) {
            return value.toUpperCase();
        }

        public static List<String> customValueParser(String value) {
            return List.of(value);
        }
    }

    private final EnvironmentAdapter envAdapterMock = mock();
    private TestSetting settings;

    @BeforeEach
    public void setup() {
        reset(envAdapterMock);

        settings = new TestSetting();
    }

    @Test
    public void testStringValueSettingSet() throws NoSuchFieldException {
        when(envAdapterMock.getValue("STRING_VALUE", "value.string")).thenReturn("found value");

        var field = TestSetting.class.getDeclaredField("STRING_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals("found value", settings.STRING_VALUE);
    }

    @Test
    public void testRequiredSettingNotSetShouldFail() throws NoSuchFieldException {
        when(envAdapterMock.getValue(any(), any())).thenReturn(null);

        var field = TestSetting.class.getDeclaredField("STRING_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        var exception = assertThrows(RuntimeException.class, () -> injector.injectMembers(settings));

        assertEquals(exception.getCause().getClass(), SettingsException.class);
    }

    @Test
    public void testNotRequiredSettingShouldReturnNull() throws NoSuchFieldException {
        when(envAdapterMock.getValue(any(), any())).thenReturn(null);

        var field = TestSetting.class.getDeclaredField("NOT_REQUIRED_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals(null, settings.NOT_REQUIRED_VALUE);
    }

    @Test
    public void testSettingWithDefaultShouldReturnTheDefaultWhenNull() throws NoSuchFieldException {
        when(envAdapterMock.getValue(any(), any())).thenReturn(null);

        var field = TestSetting.class.getDeclaredField("DEFAULT_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals("DEFAULT", settings.DEFAULT_VALUE);
    }

    @ParameterizedTest
    @ValueSource(strings = {"true", "True", "TRUE", "false"})
    public void testBooleanSettingShouldParseToBoolean(String envValue) throws NoSuchFieldException {
        when(envAdapterMock.getValue("BOOLEAN_VALUE", "value.boolean")).thenReturn(envValue);

        var field = TestSetting.class.getDeclaredField("BOOLEAN_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals(Boolean.parseBoolean(envValue.toLowerCase()), settings.BOOLEAN_VALUE);
    }

    @Test
    public void testIntegerSettingShouldParseToInteger() throws NoSuchFieldException {
        when(envAdapterMock.getValue("INTEGER_VALUE", "value.integer")).thenReturn("42");

        var field = TestSetting.class.getDeclaredField("INTEGER_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals(42, settings.INTEGER_VALUE);
    }

    @Test
    public void testCustomStringValueSettingShouldParseTheValue() throws NoSuchFieldException {
        when(envAdapterMock.getValue("CUSTOM_STRING_VALUE", "value.customString"))
                .thenReturn("found value");

        var field = TestSetting.class.getDeclaredField("CUSTOM_STRING_VALUE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals("FOUND VALUE", settings.CUSTOM_STRING_VALUE);
    }

    @Test
    public void testCustomValueTypeSettingShouldParseTheValue() throws NoSuchFieldException {
        when(envAdapterMock.getValue("CUSTOM_VALUE_TYPE", "value.customType")).thenReturn("found value");

        var field = TestSetting.class.getDeclaredField("CUSTOM_VALUE_TYPE");
        var injector = new SettingsMemberInjector<TestSetting>(TestSetting.class, field, envAdapterMock);

        injector.injectMembers(settings);

        assertEquals(List.of("found value"), settings.CUSTOM_VALUE_TYPE);
    }
}
