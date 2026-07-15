import QtQuick
import EcranJeux

Window {
    width: mainScreen.width
    height: mainScreen.height

    visible: true
    title: "EcranJeux"

    FondBiere {
        id: mainScreen

        anchors.centerIn: parent
    }

}

