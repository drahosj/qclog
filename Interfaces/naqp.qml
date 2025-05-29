import QtQuick.Layouts
import "../QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("NAQP Logging")

    LogField {
        id: nameIn
        Layout.minimumWidth: 140
        placeholderText: 'NAME'
        backgroundColor: 'plum'
    }

    LogField {
        id: stateIn
        placeholderText: 'STATE'
        backgroundColor: 'teal'
    }

    function submit(exch) {
        exch['name'] = nameIn.text;
        exch['state'] = stateIn.text;
        if (exch['state'] == "" || exch['name'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        nameIn.text = '';
        stateIn.text = '';
    }
}
