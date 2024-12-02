var msg = JSON.parse(connectorMessage.getEncodedData());

// Initialize the global message list if it doesn't exist
if (globalMap.get('messageList') == null) {
    globalMap.put('messageList', new java.util.ArrayList());
}

// Add messages to the global list
msg.forEach(function(message) {
    globalMap.get('messageList').add(JSON.stringify(message));
});