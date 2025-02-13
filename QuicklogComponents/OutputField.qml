import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "."

Rectangle {
    id: root
    property alias text: textOut.text
    property alias backgroundColor: root.color
    property string title: ''

    text: title
    color: 'grey'
    Layout.minimumHeight: 45
    Layout.minimumWidth: 200
    Layout.maximumWidth: 200
    Layout.margins: 0
    Text {
        id: textOut
        font.pointSize: 20
        font.family: 'monospace'
        anchors.centerIn: parent
    }

    MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.RightButton

        onClicked: {
            editDialog.open()
        }
    }

    EditDialog {
        id: editDialog
    }
}
