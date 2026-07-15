import QtQuick
import QtQuick.Controls

Window {
    width: 720
    height: 1280
    visible: true
    title: "Mon Application"

    // 1. LE FOND PERMANENT (Les bulles coulent sans aucune interruption)
    FondBiere {
        anchors.fill: parent
    }

    // 2. LE SYSTÈME DE NAVIGATION
    StackView {
        id: stackView
        anchors.fill: parent

        // Au lancement, le StackView charge un Item vide et transparent.
        // On ne voit donc que les bulles en arrière-plan !
        initialItem: Item {}

        // (Optionnel) Ajoute un fondu pour que les apparitions soient douces
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
        interval: 2000 // Laisse l'utilisateur admirer les bulles seules pendant 2 secondes
        running: true  // Démarre automatiquement au lancement
        repeat: false

        onTriggered: {
            // Après 2 secondes, on affiche le logo et la barre de chargement
            stackView.replace("SplashScreen.ui.qml")

            // On déclenche le chronomètre du deuxième minuteur
            timerPassageMenu.start()
        }
    }

    // 4. DEUXIÈME MINUTEUR : Passe au Menu Principal
    Timer {
        id: timerPassageMenu
        interval: 8000 // 3 secondes (le temps que ta ProgressBar se remplisse)
        running: false // IMPORTANT : Désactivé au départ, il attend le signal du 1er timer
        repeat: false

        onTriggered: {
            // La barre est pleine, on passe au menu !
            stackView.replace("MainMenu.ui.qml")
        }
    }
}
