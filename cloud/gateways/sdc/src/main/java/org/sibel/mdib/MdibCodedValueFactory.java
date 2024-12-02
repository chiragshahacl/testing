package org.sibel.mdib;

import java.util.Optional;
import org.somda.sdc.biceps.model.participant.CodedValue;

public final class MdibCodedValueFactory {
    public static CodedValue createCodedValue(String code, String symbolicName) {
        var codedValue = new CodedValue();
        Optional.ofNullable(code).ifPresent(codedValue::setCode);
        Optional.ofNullable(symbolicName).ifPresent(codedValue::setSymbolicCodeName);
        return codedValue;
    }
}
