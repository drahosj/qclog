import QtQuick.Layouts
import "QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("Field Day Logging")

    LogField {
        id: classIn
        placeholderText: 'CLASS'
        backgroundColor: 'teal'
    }

    LogField {
        id: sectionIn
        placeholderText: 'SECTION'
        backgroundColor: 'plum'
    }

    function submit(exch) {
        exch['class'] = classIn.text;
        exch['section'] = sectionIn.text;
        if (exch['class'] == "" || exch['section'] == "") {
            root.setStatus("incomplete");
            return false;
        }
        return true;
    }

    function clear() {
        classIn.text = '';
        sectionIn.text = '';
    }
}
