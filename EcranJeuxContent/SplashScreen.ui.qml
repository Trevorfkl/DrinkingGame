
/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 720
    height: 1280
    opacity: 1.0 // L'opacité maximale est 1.0 (et non 100)
    visible: true
    color: "transparent"
    radius: 0

    Rectangle {
        id: column
        x: 94
        y: 261
        color: "transparent"
        width: 550
        height: 700
        clip: false

        Text {
            id: text1
            y: 680
            color: "#ffffff"
            text: qsTr("Meeeuuuuuhh")
            font.pixelSize: 11
            anchors.horizontalCenter: parent.horizontalCenter
            font.family: "Drunk Handwriting"
            font.bold: true
        }

        ProgressBar {
            id: progressBar
            y: 398
            width: 200
            height: 10

            // 1. Il faut définir l'échelle de la barre ici !
            from: 0
            to: 100
            value: 0

            onValueChanged: {
                // S'assure que le backend est bien connecté pour éviter les crashs au démarrage
                if (typeof backend_python !== "undefined") {
                    // Math.round() transforme 45.67% en 46 pour ton script Python
                    backend_python.majProgressionChargement(Math.round(progressBar.value))
                }
            }

            indeterminate: false
            anchors.horizontalCenterOffset: 0
            wheelEnabled: false
            enabled: true
            z: 20
            scale: 2.2
            anchors.horizontalCenter: parent.horizontalCenter

            background: Rectangle {
                implicitWidth: parent.width
                implicitHeight: parent.height
                color: "#4d2e00" // Un brun foncé rappelant la bière brune
                radius: height / 2 // La moitié de la hauteur = bords parfaitement ronds !
                border.color: "#ffffff" // Une petite bordure blanche
                border.width: 1
                opacity: 0.6
            }

            // --- 2. LE REMPLISSAGE (Partie pleine) ---
            contentItem: Item {
                implicitWidth: parent.width
                implicitHeight: parent.height

                Rectangle {
                    // La magie : la largeur se calcule selon le pourcentage de remplissage
                    width: progressBar.visualPosition * parent.width
                    height: parent.height
                    radius: parent.height / 2 // Même rondeur que le fond

                    // Un beau dégradé jaune bière pour le remplissage
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop {
                            position: 0.0
                            color: "#fda301"
                        }
                        GradientStop {
                            position: 1.0
                            color: "#fedd14"
                        }
                    }
                }
            }

            // 2. Une seule animation, avec la bonne cible (progressBar)
            PropertyAnimation {
                target: progressBar
                property: "value"
                from: 0
                to: 100
                duration: 6000 // Se remplit en 3 secondes

                // Ne démarre que lorsque l'écran (root) est complètement visible
                running: root.opacity === 1.0
            }
        }
    }
}
