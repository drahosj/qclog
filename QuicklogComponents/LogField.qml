import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

TextField {
    id: root
    property alias backgroundColor: root.bgInactive
    property color bgActive
    property color bgInactive
    property string exchangeTag

    exchangeTag: ''
    bgActive: 'lightblue'
    bgInactive: 'grey'


    Layout.minimumHeight: parent.height
    Layout.margins: 0
    font.pointSize: 20
    font.family: 'monospace'
    font.capitalization: Font.AllUppercase
    placeholderTextColor: 'white'
    background: Rectangle {
        color: root.cursorVisible ? bgActive : bgInactive
    }
}
