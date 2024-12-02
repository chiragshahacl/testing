// This script executes once after a message has been processed
// Responses returned from here will be stored as "Postprocessor" in the response map

for each (connectorMessage in message.getConnectorMessages().values().toArray()) {
	if (connectorMessage.getMetaDataId() > 0 && connectorMessage.getStatus() == ERROR) {
		logger.error(
			"There was an error with the message " + 
			connectorMessage.getMessageId() + 
			" The response of the EHR was " + connectorMessage.getResponseData()
		);
	}
}

return;