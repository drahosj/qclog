import QtQuick.Layouts
import "QuicklogComponents"

LoggingWindow {
    id: root
    title: qsTr("Field Day Logging")

    LogField {
        id: classIn
        Layout.minimumWidth: 90
        placeholderText: 'CLASS'
        backgroundColor: 'teal'

        exchangeTag: 'class'
    }

    LogField {
        id: sectionIn
        Layout.minimumHeight: 45
        placeholderText: 'SECTION'
        backgroundColor: 'plum'

        exchangeTag: 'section'
    }

    onSubmit: {
        console.log("Enter pressed");
        var call = callIn.text;
        var cls = classIn.text;
        var sec = sectionIn.text;
        if (call == "" || cls == "" || sec == "") {
            root.setStatus("incomplete");
        } else {
            root.clearStatus("duplicate");
            root.clearStatus("incomplete");
            var exch = {class: cls, section: sec};
            var meta = {operator: operatorOut.text,
                        frequency: frequencyOut.text};
            logger.log(callIn.text, 
                bandOut.text, 
                modeOut.text,
                JSON.stringify(exch),
                JSON.stringify(meta));
            callIn.text = "";
            classIn.text = "";
            sectionIn.text = "";
            callIn.focus = true;
        }
    }

    onClear: {
        console.log("Escape pressed");
        callIn.text = "";
        classIn.text = "";
        sectionIn.text = "";
        root.clearStatus("duplicate");
        root.clearStatus("incomplete");
        callIn.focus = true;
    }
}
