import QtQuick.Layouts
import "../QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("IAQP Logging")

    LogField {
        id: rstSentIn
        placeholderText: 'RST sent'
        backgroundColor: 'purple'
        Layout.minimumWidth: 140
        defaultValue: '59'
    }

    LogField {
        id: rstRcvdIn
        placeholderText: 'RST rcvd'
        backgroundColor: 'blue'
        Layout.minimumWidth: 140
        defaultValue: '59'
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
        exch['rstsent'] = rstSentIn.text;
        exch['rstrcvd'] = rstRcvdIn.text;
        exch['state'] = stateIn.text;
        exch['county'] = countyIn.text;
        if (exch['state'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        if (exch['rstsent'] = "") {
            exch['rstsent'] = "59";
        }
        if (exch['rstrcvd'] = "") {
            exch['rstrcvd'] = "59";
        }
        return true;
    }

    function clear() {
        rstSentIn.text = rstSentIn.defaultValue;
        rstRcvdIn.text = rstRcvdIn.defaultValue;
        stateIn.text = stateIn.defaultValue;
        countyIn.text = countyIn.defaultValue;
    }
}
