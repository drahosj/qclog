import QtQuick.Layouts
import "../QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("IAQP Logging")

    LogField {
        id: rstIn
        placeholderText: 'RST'
        backgroundColor: 'purple'
        Layout.minimumWidth: 140
    }

    LogField {
        id: stateIn
        placeholderText: 'STATE'
        backgroundColor: 'teal'
        Layout.minimumWidth: 120
    }

    LogField {
        id: countyIn
        placeholderText: 'COUNTY'
        backgroundColor: 'plum'
        Layout.minimumWidth: 240
    }

    function submit(exch) {
        exch['rst'] = rstIn.text;
        exch['state'] = stateIn.text;
        exch['county'] = countyIn.text;
        if (exch['state'] == "" || exch['rst'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        rstIn.text = '';
        stateIn.text = '';
        countyIn.text = '';
    }
}
