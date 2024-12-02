var patientID = $s("parameters").getParameter("patientIdentifier");
var givenName = $s("parameters").getParameter("givenName");
var familyName = $s("parameters").getParameter("familyName");
var birthDate = $s("parameters").getParameter("birthDate");

channelMap.put("patientIdentifier", patientID);
channelMap.put("givenName", givenName);
channelMap.put("familyName", familyName);
channelMap.put("birthDate", birthDate);