function setConfigValue(name, resources) {
  try {
    var mapping = resources.find((resource) => resource.key === name).value;
    globalMap.put(name, mapping);
    logger.info("Value " + name + " was configured with " + mapping);
  } catch (e) {
    logger.info("The value " + name + " was not present in the response.");
  }
}

var response = connectorMessage.getResponseTransformedData();
try {
  var jsonResponse = JSON.parse(response);
  var resources = jsonResponse.resources;

  setConfigValue("MLLP_PORT", resources);
  setConfigValue("MLLP_HOST", resources);
  setConfigValue("MLLP_EXPORT_INTERVAL_MINUTES", resources);
} catch (e) {
  logger.info("Received configuration was invalid, ignoring");
}

