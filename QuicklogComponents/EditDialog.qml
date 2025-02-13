import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Dialog {
    id: root
    modal: true
    focus: true
    title: 'Set ' + parent.editTitle
    onOpened: {
        editField.focus = true
        editField.selectAll()
    }

    TextField {
        id: editField
        text: root.parent.text
        Keys.onReturnPressed: root.accept()
    }

    standardButtons: Dialog.Ok | Dialog.Cancel

    onAccepted: {
        parent.text = editField.text
    }

    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent
}

