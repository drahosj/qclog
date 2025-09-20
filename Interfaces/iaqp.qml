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
    }

    LogField {
        id: rstRcvdIn
        placeholderText: 'RST rcvd'
        backgroundColor: 'blue'
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
        exch['rstsent'] = rstSentIn.text;
        exch['rstrcvd'] = rstRcvdIn.text;
        exch['state'] = stateIn.text;
        exch['county'] = countyIn.text;
        if (exch['state'] == "" || exch['rstsent'] == "" || exch['rstrcvd'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        rstSentIn.text = '';
        rstRcvdIn.text = '';
        stateIn.text = '';
        countyIn.text = '';
    }
}
