import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    id: root
    property alias text: textOut.text
    property alias backgroundColor: root.color

    signal rightClicked()

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
            root.rightClicked()
        }
    }
}
