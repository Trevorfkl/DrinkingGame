import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: pageParametres

    // La variable qui reçoit la liste des joueurs
    property var modeleJoueurs: null

    // 1. LE TITRE
    Text {
        id: titre
        text: "⚙️ Paramètres de la partie"
        color: "white"
        font.pixelSize: 35
        font.bold: true
        anchors.top: parent.top
        anchors.topMargin: 50
        anchors.horizontalCenter: parent.horizontalCenter
    }

    // 2. LA LISTE DES JOUEURS
    ListView {
        id: listeJoueurs
        width: parent.width * 0.90 // Un peu plus large pour laisser place à la boisson
        anchors.top: titre.bottom
        anchors.topMargin: 40
        anchors.bottom: conteneurBoutons.top
        anchors.bottomMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 15
        clip: true

        model: pageParametres.modeleJoueurs

        delegate: Rectangle {
            width: listeJoueurs.width
            height: model.hasPlayer ? 90 : 0
            visible: model.hasPlayer 
            color: "#2c3e50"
            radius: 15

            RowLayout {
                anchors.fill: parent
                anchors.margins: 15
                spacing: 15
                visible: model.hasPlayer

                // 1. LE NOM DU JOUEUR
                Text {
                    text: model.playerName
                    color: "white"
                    font.pixelSize: 24
                    font.bold: true
                    Layout.preferredWidth: 130
                    elide: Text.ElideRight // Coupe le texte avec des "..." s'il est trop long
                }

                // ==========================================
                // 2. LE SÉLECTEUR DE BOISSON (Nouveau !)
                // ==========================================
                Rectangle {
                    id: btnBoisson
                    Layout.preferredWidth: 140
                    Layout.preferredHeight: 50
                    radius: 10
                    color: "#34495e" // Un fond légèrement différent
                    border.color: "#7f8c8d"
                    border.width: 2

                    // Ton "menu" de boissons possibles
                    property var listeBoissons: ["🍺 Bière", "🍷 Vin", "🥃 Fort", "🍹 Cocktail", "💧 Eau"]
                    property int indexBoisson: 0 // Par défaut, on commence à "Bière"

                    Text {
                        text: btnBoisson.listeBoissons[btnBoisson.indexBoisson]
                        color: "white"
                        font.pixelSize: 18
                        font.bold: true
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        anchors.fill: parent
                        onClicked: {
                            // On passe à la boisson suivante, et on revient à zéro (Bière) quand on atteint la fin
                            btnBoisson.indexBoisson = (btnBoisson.indexBoisson + 1) % btnBoisson.listeBoissons.length
                        }
                    }
                }

                // 3. LE SLIDER (La jauge)
                Slider {
                    id: sliderConso
                    from: 1
                    to: 20
                    stepSize: 1
                    value: 5
                    Layout.fillWidth: true
                }

                // 4. L'AFFICHAGE DU SLIDER
                Text {
                    text: sliderConso.value + " 💧"
                    color: "#f39c12"
                    font.pixelSize: 26
                    font.bold: true
                    Layout.preferredWidth: 70
                    horizontalAlignment: Text.AlignRight
                }
            }
        }
    }

    // 3. LES BOUTONS EN BAS (Retour & Commencer)
    RowLayout {
        id: conteneurBoutons
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 50
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 40

        // Bouton RETOUR
        Rectangle {
            width: 200
            height: 70
            radius: 35
            color: "#e74c3c"
            
            Text {
                text: "⬅️ Retour"
                color: "white"
                font.pixelSize: 22
                font.bold: true
                anchors.centerIn: parent
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    console.log("⬅️ [QML] Retour au menu principal")
                    stackView.pop() 
                }
            }
        }

        // Bouton COMMENCER LA PARTIE
        Rectangle {
            width: 250
            height: 70
            radius: 35
            color: "#2ecc71"
            
            Text {
                text: "🍻 C'EST PARTI !"
                color: "white"
                font.pixelSize: 22
                font.bold: true
                anchors.centerIn: parent
            }

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    console.log("🎮 [QML] Lancement officiel de la partie avec les paramètres !")

                    // On crée une liste pour stocker les réglages de chaque joueur
                    let parametresPartie = []

                    // On parcourt tous les éléments du modèle
                    for (let i = 0; i < modeleJoueurs.count; i++) {
                        let joueur = modeleJoueurs.get(i)
                        if (joueur.hasPlayer) {
                            // Note: On peut retrouver l'enfant dans la ListView, ou passer par une structure propre.
                            // Pour faire simple et robuste, passons les données de base pour l'instant :
                            parametresPartie.push({
                                "nom": joueur.playerName,
                                "sliderValue": 10 // On va lier ça proprement juste en bas
                            })
                        }
                    }

                    // On envoie tout à Python
                    // backend_python.lancerPartie(JSON.stringify(parametresPartie))
                }
            }
        }
    }
}