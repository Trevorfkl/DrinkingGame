import QtQuick
import QtQuick.Controls
import EcranJeux

Window {
    id: window
    width: 1280 // Largeur native de l'écran physique (horizontale)
    height: 800 // Hauteur native
    visibility: Window.FullScreen
    visible: true
    title: "EcranJeux"
    color: "black"

    // --- LE CONTENEUR MAGIQUE QUI TOURNE LE JEU ---
    Item {
        width: 800  // Le format vertical de ton jeu
        height: 1280
        anchors.centerIn: parent
        rotation: 270 // (Essaie 90 si c'est à l'envers !)

        // 1. LE FOND
        FondBiere {
            id: mainScreen
            anchors.fill: parent
        }

        // 2. LE SYSTÈME DE NAVIGATION
        StackView {
            id: stackView
            anchors.fill: parent

            initialItem: Item { }

            replaceEnter: Transition { PropertyAnimation { property: "opacity"; from: 0; to: 1; duration: 500 } }
            replaceExit: Transition { PropertyAnimation { property: "opacity"; from: 1; to: 0; duration: 500 } }
        }

        // 3. TES DEUX MINUTEURS
        Timer {
            id: timerApparitionSplash
            interval: 2000
            running: true
            repeat: false
            onTriggered: {
                console.log("Chargement du Splash Screen...")
                stackView.replace("SplashScreen.ui.qml")
                timerPassageMenu.start()
            }
        }

        Timer {
            id: timerPassageMenu
            interval: 8000
            running: false
            repeat: false
            onTriggered: {
                console.log("Chargement du Menu Principal...")
                stackView.replace("MainMenu.qml")
            }
        }
    } // Fin du conteneur magique
}