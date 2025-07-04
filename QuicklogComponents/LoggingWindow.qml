import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "."
import "../helpers.js" as Helpers

Window {
    id: root
    width: 1400
    height: 45
    visible: true
    property string baseTitle: qsTr("Minimal Logger")
    title: baseTitle

    default property alias fields: logFields.data

    property alias callIn: callIn
    property alias modeOut: modeOut
    property alias bandOut: bandOut
    property alias frequencyOut: frequencyOut
    property alias operatorOut: operatorOut

    function populateRigData(band, mode, freq) {
        if (band) {
            bandOut.text = band;
        }
        if (mode) {
            modeOut.text = mode;
        }
        if (freq) {
            frequencyOut.text = freq;
        }
    }

    function setup(operator) {
        if (operator) {
            operatorOut.text = operator;
        }
        callIn.focus = true;
    }

    function setCall(call) {
        callIn.text = call;
        logger.checkDupe(callIn.text, bandOut.text, modeOut.text);
    }

    function setStatus(text) {
        Helpers.addStatusMessage(text);
        root.updateStatus();
    }

    function clearStatus(text) {
        Helpers.deleteStatusMessage(text);
        root.updateStatus();
    }

    function logged(uuid) {
        if (uuid) {
            console.log("UI got response of logged qso " + uuid);
            root.clearFields()
        } else {
            console.log("Logger rejected qso.");
            root.setStatus('duplicate');
        }
    }

    function localLogged(qso) {
        console.log("UI got logged QSO: " + JSON.stringify(qso));
        updateTitleStatus();
    }

    function remoteLogged(qso) {
        console.log("UI got remote QSO: " + JSON.stringify(qso));
        updateTitleStatus();
    }

    function updateTitleStatus() {
        console.log("Updating title status.")
        var l_qso_call = logger.lastQso["callsign"];
        var l_qso_ts = logger.lastQso["timestamp"];
        var r_qso_call = net.lastQso["callsign"];
        var r_qso_by = net.lastQso["logged_by"];
        var r_qso_ts = net.lastQso["timestamp"];
        var t = `${baseTitle} (${qclog.stationName})`;
        if (l_qso_call) {
            l_qso_ts = l_qso_ts.split(' ')[1]
            t = `${t} - Logged ${l_qso_call} at ${l_qso_ts}UTC`
        }
        if (r_qso_call) {
            r_qso_ts = r_qso_ts.split(' ')[1]
            t = `${t} - ${r_qso_call} logged by ${r_qso_by} at ${r_qso_ts}UTC`
        }
        title = t
    }


    function updateStatus() {
        var st = Helpers.getCurrentStatus()
        if (st != "") {
            statusOut.text = st;
            statusBox.visible = true;
        } else {
            statusBox.visible = false;
        }
    }

    function clearFields() {
        callIn.text = '';
        callIn.focus = true;
        root.clearStatus("duplicate");
        root.clearStatus("incomplete");
        root.clear();
    }

    function injectTestQso(call, exch) {
        callIn.text = call;
        // TODO implement exchange
        entryRow.handleReturnPressed(true);
    }

    RowLayout {
        spacing: 0
        id: entryRow

        OutputField {
            backgroundColor: 'green'
            id: modeOut
            title: 'Mode'
	    Layout.minimumWidth: 100
	    Layout.maximumWidth: 100
        }

        OutputField {
            backgroundColor: 'plum'
            id: bandOut
            title: 'Band'
	    Layout.minimumWidth: 80
	    Layout.maximumWidth: 80
        }

        OutputField {
            backgroundColor: 'teal'
            id: frequencyOut
            title: 'Frequency'
        }

        OutputField {
            backgroundColor: 'darkgrey'
            Layout.rightMargin: 20
            id: operatorOut
            title: 'Operator'
	    Layout.minimumWidth: 140
	    Layout.maximumWidth: 140
        }

        LogField {
            id: callIn
            Layout.minimumWidth: 200
            placeholderText: 'CALL'
            backgroundColor: 'grey'

            onTextEdited: function() {
                logger.checkDupe(callIn.text, bandOut.text, modeOut.text);
            }
        }

        Rectangle {
            Layout.minimumWidth: 10
        }

        RowLayout {
            spacing: 0
            id: logFields
            Layout.fillWidth: true
        }

        Rectangle {
            id: statusBox
            color: 'red'
            Layout.minimumHeight: 45
            Layout.minimumWidth: 240
            Layout.maximumWidth: 240
            Layout.margins: 0
            Layout.leftMargin: 20
            visible: false
            Text {
                id: statusOut
                font.pointSize: 12
                font.family: 'monospace'
                anchors.centerIn: parent
                text: ''
            }
        }

        Keys.onReturnPressed: (event) => {
            var force = event.modifiers & Qt.ControlModifier;
            handleReturnPressed(force);
            event.accepted = true;
        }

        function handleReturnPressed(force) {
            var exch = {};
            var call = callIn.text;
            if ((call != '') && (root.submit(exch) || force)) {
                var meta = {operator: operatorOut.text,
                frequency: frequencyOut.text};
                root.clearStatus("duplicate");
                root.clearStatus("incomplete");

                logger.log(callIn.text,
                bandOut.text,
                modeOut.text,
                JSON.stringify(exch),
                JSON.stringify(meta), force);
            }
        }

        Keys.onEscapePressed: (event) => {
            clearFields();
            event.accepted = true;
        }
    }
}
