function needToSend() {
	var lastSent = globalMap.get('lastSent');
	
	if (lastSent == null ) {
		return true;
	}
	var intervalMinutes = parseInt(globalMap.get("MLLP_EXPORT_INTERVAL_MINUTES"));
	var currentTime = Date.now();
	var intervalMilliseconds = intervalMinutes * 60 * 1000;

	
	return currentTime - lastSent >= intervalMilliseconds;

}


function processMessages() {
    var messageList = globalMap.get('messageList');

    if (messageList != null && !messageList.isEmpty()) {
        for (var i = 0; i < messageList.size(); i++) {
            var message = messageList.get(i);
            router.routeMessage('MLLP Sender', message);
        }

        messageList.clear();
    }

}

if (needToSend()) {
	processMessages();
	globalMap.put('lastSent', Date.now());
}
