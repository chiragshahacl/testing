package org.sibel.constants;

import java.util.List;

public class MdpwsConfig {
    public static final String MDPWS_CONTEXT_PATH = "org.sibel.mdib.mdpws";
    public static final String MDPWS_SCHEMA_PATH = "MDPWS.xsd";

    public static final List<String> ALLOWED_MDIB_VERSIONING_ATTRIBUTES = List.of(
            "DescriptorVersion",
            "StateVersion",
            "MdibVersion",
            "SequenceId",
            "InstanceId",
            "BindingMdibVersion",
            "UnbindingMdibVersion");
}
