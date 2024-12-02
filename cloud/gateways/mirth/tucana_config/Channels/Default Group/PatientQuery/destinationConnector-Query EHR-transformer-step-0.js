tmp['MSH']['MSH.7']['MSH.7.1'] = DateUtil.getCurrentDate('yyyyMMddHHmmss');
tmp['MSH']['MSH.10']['MSH.10.1'] = UUIDGenerator.getUUID();
tmp['QPD']['QPD.2']['QPD.2.1'] = UUIDGenerator.getUUID();

var patientIdentifier = sourceMap.get("patientIdentifier");
var givenName = sourceMap.get("givenName");
var familyName = sourceMap.get("familyName");
var birthDate = sourceMap.get("birthDate");

var qpd3 = '';
if (patientIdentifier) {
    qpd3 = '@PID.3.1^' + patientIdentifier;
} else if (givenName && familyName) {
    qpd3 = givenName + '^' + familyName;
    if (birthDate) {
        qpd3 += '^' + birthDate;
    }
}

tmp['QPD']['QPD.3']['QPD.3.1'] = qpd3;