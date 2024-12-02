/**
 * Route a JSON message to channel by channel id and include the metadata for tracking message flow
 * @param {string} cid
 * @param {Object} json
 */
const routeJsonMsg = (cid, json) => {
  if (!json.metadata) {
    json.metadata = {}
    var sourceChannelIds = sourceMap.get('sourceChannelIds') || sourceMap.get('sourceChannelId')
    var sourceMessageIds = sourceMap.get('sourceMessageIds') || sourceMap.get('sourceMessageId')
    if (sourceChannelIds && sourceMessageIds) {
      json.metadata.sourceChannelIds = sourceChannelIds.toArray ? sourceChannelIds.toArray() : [sourceChannelIds]
      json.metadata.sourceMessageIds = sourceMessageIds.toArray ? sourceMessageIds.toArray() : [sourceMessageIds]
      json.metadata.sourceChannelNames = json.metadata.sourceChannelIds.map(id => ChannelUtil.getChannelName(id))
    } else {
      json.metadata.sourceChannelIds = []
      json.metadata.sourceMessageIds = []
      json.metadata.sourceChannelNames = []
    }
  }
  json.metadata.channelId = channelId
  json.metadata.channelName = channelName
  json.metadata.messageId = connectorMessage.getMessageId()
  json.metadata.errorMessage = json.errorMessage || ''
  json.metadata.errorStack = json.errorStack || ''

  json.metadata.sourceChannelIds.push(channelId)
  json.metadata.sourceMessageIds.push(json.metadata.messageId)
  json.metadata.sourceChannelNames.push(channelName)
  return router.routeMessage(cid, JSON.stringify(json, null, 2))
}

var contextPath = sourceMap.get('contextPath').toString();

if (contextPath == '/query/patient' || contextPath == '/query/patient/') {
	var patientIdentifier = $s("parameters").getParameter("patientIdentifier");
	var givenName = $s("parameters").getParameter("givenName");
	var familyName = $s("parameters").getParameter("familyName");
	var birthDate = $s("parameters").getParameter("birthDate");
	var params = {
		patientIdentifier: patientIdentifier,
		givenName: givenName,
		familyName: familyName,
		birthDate: birthDate
	};
    return router.routeMessage('PatientQuery', new RawMessage(connectorMessage.toString(), null, params));
} else if (contextPath == '/consume' || contextPath == '/consume/') {
    var response = routeJsonMsg('HTTP Server', JSON.parse(connectorMessage.getEncodedData()));
    if (response.getStatus() === ERROR){
    		logger.error("Something went wrong" + response.getStatusMessage());
    		responseStatus = '500';
		return '{"message": "Something went wrong"}';
    	}
    	responseStatus = '200';
    	return '{"message": "Success"}';
} else {
    	logger.error("Invalid path was requested " + contextPath);
	responseStatus = '404';
	return '{"message": "Unknown endpoint"}';
}