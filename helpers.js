var activeMessages = {
    duplicate: false,
    incomplete: false,
    rigerror: false
}

function addStatusMessage(message) {
    console.log("addStatusMessage(): message: " + message);
    activeMessages[message] = true;
    console.log("addStatusMessage(): Status messages: " + JSON.stringify(activeMessages));
}

function deleteStatusMessage(message) {
    console.log("deleteStatusMessage(): message: " + message);
    activeMessages[message] = false;
    console.log("deleteStatusMessage(): Status messages: " + JSON.stringify(activeMessages));
}

function getCurrentStatus() {
    console.log("deleteStatusMessage(): Status messages: " + JSON.stringify(activeMessages));
    if (activeMessages.duplicate) {
        return "Duplicate entry!";
    } else if (activeMessages.incomplete) {
        return "Incomplete entry!";
    } else if (activeMessages.rigerror) {
        return "Rig communication error!";
    } else {
        return "";
    }
}

function callInEdited() {
    console.log("callInEdited");
}
