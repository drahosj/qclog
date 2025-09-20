import QtQuick.Layouts
import "../QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("IAQP Logging")

    LogField {
        id: rstIn
        text: '599'
        placeholderText: 'RST'
        backgroundColor: 'plum'
    }

    LogField {
        id: stateIn
        placeholderText: 'STATE/COUNTY/DX'
        backgroundColor: 'teal'
    }

    function submit(exch) {
        exch['rst'] = rstIn.text;
        exch['state'] = stateIn.text;
        if (exch['state'] == "" || exch['rst'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        rstIn.text = '599';
        stateIn.text = '';
    }
}
