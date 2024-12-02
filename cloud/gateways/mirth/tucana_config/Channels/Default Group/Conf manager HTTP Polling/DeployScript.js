// Retrieve the value of the AUTH_TOKEN environment variable
const authToken = Packages.java.lang.System.getenv("AUTH_TOKEN");

// Store the authToken value in the global channel map
globalChannelMap.put("AUTH_TOKEN", authToken);

// Log a message to confirm that the variable was stored
logger.info("Stored AUTH_TOKEN value in global channel map: " + authToken);

// Retrieve the value of the CONF_SERVICE_URL environment variable
const confServiceUrl = Packages.java.lang.System.getenv("CONF_SERVICE_URL");

// Store the authToken value in the global channel map
globalChannelMap.put("CONF_SERVICE_URL", confServiceUrl);

// Log a message to confirm that the variable was stored
logger.info(
  "Stored CONF_SERVICE_URL value in global channel map: " + confServiceUrl,
);

// Retrieve the value of the MLLP host and port environment variable
const mllpHost = Packages.java.lang.System.getenv("MLLP_HOST");
const mllpPort = Packages.java.lang.System.getenv("MLLP_PORT");
const exportIntervalMinutes = Packages.java.lang.System.getenv(
  "MLLP_EXPORT_INTERVAL_MINUTES",
);

// Store the values in the global map
globalMap.put("MLLP_HOST", mllpHost);
globalMap.put("MLLP_PORT", mllpPort);
globalMap.put("MLLP_EXPORT_INTERVAL_MINUTES", exportIntervalMinutes);

// Log a message to confirm that the variable was stored
logger.info(
  "Stored MLLP value in global channel map: " + mllpHost + ":" + mllpPort,
);
logger.info("Exporting to EHR every " + exportIntervalMinutes + " minutes");

