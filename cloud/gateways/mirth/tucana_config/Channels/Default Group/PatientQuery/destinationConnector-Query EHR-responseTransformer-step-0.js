if (response.getError() != null) {
	logger.error("There was an error exporting the message " + response.getError());
}

var responseObj = {};

responseObj.resources = [];

try {
	for (var i = 0; i < msg["PID"].length(); i++) {
			var patient = {};
			patient.patientIdentifiers = [];
	
		  for (var j = 0; j < msg["PID"]["PID.3"].length(); j++) {
		  	if (msg["PID"][i]["PID.3"][j] !== undefined) {
		  		patient.patientIdentifiers.push(msg["PID"][i]["PID.3"][j]["PID.3.1"].toString());	
		  	}
		  }
		  
		  patient.givenName = msg["PID"][i]["PID.5"]["PID.5.2"].toString();
		  patient.familyName = msg["PID"][i]["PID.5"]["PID.5.1"].toString();
		  patient.birthDate = msg["PID"][i]["PID.7"]["PID.7.1"].toString();
		  patient.gender = msg["PID"][i]["PID.8"]["PID.8.1"].toString();
		
		  responseObj.resources.push(patient);
	}
	msg = JSON.stringify(responseObj);
	responseMap.put('httpResponseStatusCode', '200');	
} catch(e) {
	logger.error("Error on response from EHR " + e.toString());
	responseMap.put('httpResponseStatusCode', '502');
}