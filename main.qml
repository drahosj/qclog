import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Window {
    id: root
    width: 640
    height: 45
    visible: true
    title: qsTr("Minimal Logger")

    signal doLog(string callsign, string band, string mode, string exch)
    signal checkDupe(string callsign, string band, string mode)

    function setup(band, mode, operator) {
        bandOut.text = band;
	modeOut.text = mode;
	mycallOut.text = operator;
        callIn.focus = true;
    }

    function setStatus(text) {
        statusOut.text = text;
        statusBox.visible = true;
    }

    RowLayout {
        spacing: 0

        Rectangle {
            color: 'green'
            Layout.minimumHeight: 45
            Layout.minimumWidth: 70
            Layout.maximumWidth: 70
            Layout.margins: 0
            Text {
                id: modeOut
                font.pointSize: 20
                font.family: 'monospace'
                anchors.centerIn: parent
                text: 'SSB'
            }
        }

        Rectangle {
            color: 'plum'
            Layout.minimumHeight: 45
            Layout.minimumWidth: 65
            Layout.maximumWidth: 65
            Layout.margins: 0
            Text {
                id: bandOut
                font.pointSize: 20
                font.family: 'monospace'
                anchors.centerIn: parent
                text: '20'
            }
        }

        Rectangle {
            color: 'teal'
            Layout.minimumHeight: 45
            Layout.minimumWidth: 200
            Layout.maximumWidth: 200
            Layout.margins: 0
            Text {
                id: frequencyOut
                font.pointSize: 20
                font.family: 'monospace'
                anchors.centerIn: parent
                text: '14100000'
            }
        }

        Rectangle {
            color: 'darkgrey'
            Layout.minimumHeight: 45
            Layout.minimumWidth: 200
            Layout.maximumWidth: 200
            Layout.margins: 0
            Text {
                id: mycallOut
                font.pointSize: 20
                font.family: 'monospace'
                anchors.centerIn: parent
                text: 'MYCALL'
            }
        }

        TextField {
            id: callIn
            Layout.minimumHeight: 45
            Layout.minimumWidth: 200
            Layout.maximumWidth: 200
            Layout.margins: 0
	    Layout.leftMargin: 20
            font.pointSize: 20
            font.family: 'monospace'
            font.capitalization: Font.AllUppercase
            placeholderText: 'CALL'
            placeholderTextColor: 'white'
            background: Rectangle {
                color: callIn.cursorVisible ? 'lightblue' : 'grey'
            }
	    onTextEdited: function() {
	        console.log("onTextEdited")
	        statusBox.visible = false;
                root.checkDupe(callIn.text, bandOut.text, modeOut.text);
	    }
        }

        TextField {
            id: classIn
            Layout.minimumHeight: 45
            Layout.minimumWidth: 90
            Layout.maximumWidth: 90
            Layout.margins: 0
            font.pointSize: 20
            font.family: 'monospace'
            font.capitalization: Font.AllUppercase
            placeholderText: 'CLASS'
            placeholderTextColor: 'white'
            background: Rectangle {
                color: classIn.cursorVisible ? 'lightblue' : 'teal'
            }
        }

        TextField {
            id: sectionIn
            Layout.minimumHeight: 45
            Layout.minimumWidth: 130
            Layout.maximumWidth: 130
            Layout.margins: 0
            font.pointSize: 20
            font.family: 'monospace'
            font.capitalization: Font.AllUppercase
            placeholderText: 'SECTION'
            placeholderTextColor: 'white'
            background: Rectangle {
                color: sectionIn.cursorVisible ? 'lightblue' : 'plum'
            }
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

        Keys.onPressed: (event) => {
            console.log("Key press passed to layout " + event.key);
            if (event.key == Qt.Key_Return) {
                console.log("Enter pressed");
		var call = callIn.text;
		var cls = classIn.text;
		var sec = sectionIn.text;
		if (call == "" || cls == "" || sec == "") {
		    statusOut.text = "Incomplete log entry!"
		    statusBox.visible = true;
		} else {
		    var exch = {class: cls, section: sec};
		    root.doLog(callIn.text, 
		        bandOut.text, 
		        modeOut.text,
		        JSON.stringify(exch));
		    callIn.text = "";
		    classIn.text = "";
		    sectionIn.text = "";
		    callIn.focus = true;
		    statusBox.visible = false;
	        }
            }
            if (event.key == Qt.Key_Escape) {
                console.log("Escape pressed");
                callIn.text = "";
                classIn.text = "";
                sectionIn.text = "";
                callIn.focus = true;
		statusBox.visible = false;
            }
        }
    }
}
