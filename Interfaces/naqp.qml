import QtQuick.Layouts
import "../QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("NAQP Logging")

    LogField {
        id: stateIn
        placeholderText: 'STATE'
        backgroundColor: 'teal'
    }

    LogField {
        id: nameIn
        placeholderText: 'NAME'
        backgroundColor: 'plum'
    }

    function submit(exch) {
        exch['state'] = stateIn.text;
        exch['name'] = stateIn.text;
        if (exch['state'] == "" || exch['name'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        stateIn.text = '';
        nameIn.text = '';
    }
}
