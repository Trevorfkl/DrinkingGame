import QtQuick
import QtQuick.Controls
import EcranJeux

Window {
    id: window
    width: 720
    height: 1280
    visible: true
    title: "EcranJeux"

    // 1. LE FOND PERMANENT (Les bulles coulent sans aucune interruption)
    FondBiere {
        id: mainScreen
        anchors.fill: parent
    }

    // 2. LE SYSTÈME DE NAVIGATION
    StackView {
        id: stackView
        anchors.fill: parent

        // Élément invisible au départ pour laisser voir les bulles
        initialItem: Item {
            width: 720
            height: 1280
        }

        // Les fondus d'apparition
        replaceEnter: Transition {
            PropertyAnimation { property: "opacity"; from: 0; to: 1; duration: 500 }
        }
        replaceExit: Transition {
            PropertyAnimation { property: "opacity"; from: 1; to: 0; duration: 500 }
        }
    }

    // 3. PREMIER MINUTEUR : Fait apparaître le SplashScreen
    Timer {
        id: timerApparitionSplash
        interval: 2000
        running: true
        repeat: false

        onTriggered: {
            console.log("Chargement du Splash Screen...")
            stackView.replace("SplashScreen.ui.qml") // (ou ton nom de fichier exact)
            timerPassageMenu.start()
        }
    }

    // 4. DEUXIÈME MINUTEUR : Passe au Menu Principal
    Timer {
        id: timerPassageMenu
        interval: 8000
        running: false
        repeat: false

        onTriggered: {
            console.log("Chargement du Menu Principal...")
            stackView.replace("MainMenu.qml") // On appelle bien notre fichier logique !
        }
    }
}
