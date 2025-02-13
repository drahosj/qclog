import QtQuick
import QtQuick.Layouts
import "../QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("Pota Logging")

    LogField {
        id: rstSent
        placeholderText: 'RST>'
        backgroundColor: 'teal'
    }

    LogField {
        id: rstRecvd
        placeholderText: 'RST<'
        backgroundColor: 'plum'
        width: 20
    }

    LogField {
        id: qth
        placeholderText: 'QTH'
        backgroundColor: 'blue'
    }

    LogField {
        id: park
        placeholderText: 'P2P'
        backgroundColor: 'teal'
        Layout.minimumWidth: 150
    }

    LogField {
        id: notes
        placeholderText: 'Notes'
        font.capitalization: Font.MixedCase
        Layout.minimumWidth: 300
    }

    function submit(exch) {
        exch.rst_sent = rstSent.text;
        exch.rst_received = rstRecvd.text;
        exch.qth = qth.text;
        exch.p2p_park = park.text;
        exch.notes = notes.text;
        if (exch.rst_sent == "" || exch.rst_received == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        rstSent.text = '';
        rstRecvd.text = '';
        qth.text = '';
        park.text = '';
        notes.text = '';
    }
}
