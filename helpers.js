var statusMessage = [];

function addStatusMessage(message) {
    statusMessage.push(message);
}

function deleteStatusMessage(message) {
    var i = statusMessage.indexOf(message);
    statusMessage.splice(i);
}

function getCurrentStatus() {
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
