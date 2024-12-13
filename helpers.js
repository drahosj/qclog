var statusMessage = [];

function addStatusMessage(message) {
    console.log("addStatusMessage(): message: " + message);
    statusMessage.push(message);
    console.log("addStatusMessage(): Status messages: " + statusMessage);
}

function deleteStatusMessage(message) {
    console.log("deleteStatusMessage(): message: " + message);
    console.log("deleteStatusMessage(): Status messages: " + statusMessage);
    var i;
    while ((i = statusMessage.indexOf(message)) != -1) {
        statusMessage.splice(i, 1);
    }
    console.log("deleteStatusMessage(): Status messages: " + statusMessage);
}

function getCurrentStatus() {
    console.log("getCurrentStatus(): Status messages: " + statusMessage);
    if (statusMessage.length) {
        return statusMessage[statusMessage.length - 1];
    } else {
        return "";
    }
}

function callInEdited() {
    console.log("callInEdited");
    root.clearStatus("Duplicate entry!");
    root.checkDupe(callIn.text, bandOut.text, modeOut.text);
}
