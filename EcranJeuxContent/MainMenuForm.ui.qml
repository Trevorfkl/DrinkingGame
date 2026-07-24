import QtQuick
import QtQuick.Controls

Item {
    id: root
    width: 720
    height: 1280

    // --- CONTRÔLEUR DE TEST VISUEL ---
    // Change ce texte pour voir les différents menus s'afficher :
    // "base"     -> Créer un compte OU Bouton Sélectionner
    // "options"  -> 🛒, Modifier, Pu Capable 🤮
    // "modifier" -> Le menu avec le Slider et les consommations
    property string etatPanneau: "base"
    property alias clicSelectionner: btnSelectionner
    property alias clicCreer: btnCreer
    property alias carrouselModel: joueursModel
    property alias indexCarrousel: carrousel.currentIndex
    property alias texteChampNom: champNom.text
    property alias clicRetour: btnRetour
    property alias clicEnregistrer: btnEnregistrer
    property alias clicModifier: btnModifier
    property alias clicPoubelle: btnPoubelle
    property bool placeActuelleOccupee: false // Notre interrupteur magique

    // --- 1. LES DONNÉES ---
    ListModel {
        id: joueursModel
        ListElement {
            hasPlayer: true
            playerName: "Trévys"
            coins: 450
            partiesJouees: 12
            gorgees: 84
        }
        ListElement {
            hasPlayer: false
            playerName: ""
            coins: 0
            partiesJouees: 0
            gorgees: 0
        }
        ListElement {
            hasPlayer: false
            playerName: ""
            coins: 0
            partiesJouees: 0
            gorgees: 0
        }
    }

    // --- 2. LE CARROUSEL ---
    PathView {
        id: carrousel
        width: parent.width
        height: 420
        anchors.top: parent.top
        anchors.topMargin: 100

        model: joueursModel
        pathItemCount: 3
        preferredHighlightBegin: 0.5
        preferredHighlightEnd: 0.5
        highlightRangeMode: PathView.StrictlyEnforceRange
        interactive: true

        delegate: Item {
            id: carteDelegate
            width: 320
            height: 380
            property bool estOccupe: hasPlayer

            scale: PathView.itemScale
            opacity: PathView.itemOpacity
            z: PathView.itemZ

            Rectangle {
                anchors.fill: parent
                radius: 20
                color: "#fdf5e6"
                border.color: "#fda301"
                border.width: 2

                // --- Si EMPLACEMENT LIBRE ---
                Column {
                    anchors.centerIn: parent
                    spacing: 20
                    visible: !hasPlayer

                    Text {
                        text: "?"
                        font.pixelSize: 80
                        color: "#e0d5c1"
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                    Text {
                        text: "Libre"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#a0a0a0"
                        anchors.horizontalCenter: parent.horizontalCenter
                    }
                }

                // --- Si EMPLACEMENT OCCUPÉ ---
                Column {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 15
                    visible: hasPlayer

                    Item {
                        width: parent.width
                        height: 80

                        Rectangle {
                            width: 60
                            height: 60
                            radius: 30
                            color: "#fda301"
                            anchors.verticalCenter: parent.verticalCenter

                            Text {
                                text: playerName !== "" ? playerName.charAt(
                                                              0) : ""
                                font.pixelSize: 30
                                color: "white"
                                font.bold: true
                                anchors.centerIn: parent
                            }
                        }

                        Text {
                            text: playerName
                            font.pixelSize: 28
                            font.bold: true
                            color: "#4d2e00"
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.left: parent.left
                            anchors.leftMargin: 80
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 2
                        color: "#f0e6d2"
                    }

                    Row {
                        spacing: 10
                        Text {
                            text: "🪙"
                            font.pixelSize: 24
                        }
                        Text {
                            text: coins + " Pièces"
                            font.pixelSize: 22
                            color: "#4d2e00"
                            font.bold: true
                        }
                    }

                    Row {
                        spacing: 10
                        Text {
                            text: "🍺"
                            font.pixelSize: 24
                        }
                        Text {
                            text: gorgees + " Gorgées bues"
                            font.pixelSize: 20
                            color: "#666666"
                        }
                    }
                }
            }
        }

        path: Path {
            startX: -100
            startY: carrousel.height / 2
            PathAttribute {
                name: "itemScale"
                value: 0.6
            }
            PathAttribute {
                name: "itemOpacity"
                value: 0.4
            }
            PathAttribute {
                name: "itemZ"
                value: 0
            }

            PathLine {
                x: carrousel.width / 2
                y: carrousel.height / 2
            }
            PathAttribute {
                name: "itemScale"
                value: 1.0
            }
            PathAttribute {
                name: "itemOpacity"
                value: 1.0
            }
            PathAttribute {
                name: "itemZ"
                value: 10
            }

            PathLine {
                x: carrousel.width + 100
                y: carrousel.height / 2
            }
            PathAttribute {
                name: "itemScale"
                value: 0.6
            }
            PathAttribute {
                name: "itemOpacity"
                value: 0.4
            }
            PathAttribute {
                name: "itemZ"
                value: 0
            }
        }
    }

    // --- 3. LE PANNEAU DYNAMIQUE DES BOUTONS ---
    Item {
        id: zoneBoutons
        width: parent.width
        anchors.top: carrousel.bottom
        anchors.bottom: parent.bottom
        anchors.topMargin: 20

        property bool centreOccupe: carrousel.currentItem ? carrousel.currentItem.estOccupe : false

        // ==========================================
        // ÉTAT A : MENU DE BASE
        // ==========================================
        Item {
            anchors.fill: parent
            visible: root.etatPanneau === "base"

            Column {
                anchors.top: parent.top
                anchors.topMargin: 20
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 15
                visible: !zoneBoutons.centreOccupe

                TextField {
                    id: champNom
                    width: 300
                    height: 50
                    placeholderText: "Entrez votre nom..."
                    color: "black"
                    font.pixelSize: 18
                    horizontalAlignment: TextInput.AlignHCenter
                    background: Rectangle {
                        color: "white"
                        radius: 25
                        border.color: "#fda301"
                        border.width: 2
                    }
                }

                // Le bouton fusionné qui utilise le style de ton ancien btnCreer
                Button {
                    id: btnCreer
                    width: 300
                    height: 50
                    
                    background: Rectangle {
                        radius: 25
                        color: "#4d2e00"
                    }
                    
                    contentItem: Text {
                        text: "AJOUTER"
                        color: "white"
                        font.bold: true
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    onClicked: {
                        if (champNom.text !== "") {
                            // On appelle le script Python (Emplacement 1, Nom tapé)
                            backend_python.nouveau_joueur_ajoute(1, champNom.text)
                            
                            // On vide le champ après l'envoi
                            champNom.text = ""
                        }
                    }
                }
            }

            // LE BOUTON SÉLECTIONNER
            Rectangle {
                id: btnSelectionner
                width: 300
                height: 60
                radius: 30
                color: "#fda301"
                anchors.top: parent.top
                anchors.topMargin: 20
                anchors.horizontalCenter: parent.horizontalCenter
                visible: zoneBoutons.centreOccupe
                
                Text {
                    text: "SÉLECTIONNER"
                    color: "white"
                    font.bold: true
                    font.pixelSize: 20
                    anchors.centerIn: parent
                }
            }
        }

        // ==========================================
        // ÉTAT B : OPTIONS DU JOUEUR
        // ==========================================
        Column {
            anchors.top: parent.top
            anchors.topMargin: 10
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 15
            visible: root.etatPanneau === "options"

            Rectangle {
                id: btnModifier
                width: 200 // J'ai un peu élargi à 200 pour que ça fasse de beaux boutons de menu !
                height: 60
                radius: 30
                color: "#4d2e00"
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    text: "Modifier"
                    color: "white"
                    font.bold: true
                    font.pixelSize: 18
                    anchors.centerIn: parent
                }
            }

            Rectangle {
                width: 60
                height: 60
                radius: 30
                color: "#fda301"
                anchors.horizontalCenter: parent.horizontalCenter // Garde le panier bien centré

                Text {
                    text: "🛒"
                    font.pixelSize: 30
                    anchors.centerIn: parent
                }
            }

            Rectangle {
                id: btnPoubelle
                width: 200
                height: 60
                radius: 30
                color: "#cc0000"
                anchors.horizontalCenter: parent.horizontalCenter

                Text {
                    text: "Pu Capable 🤮" // Le bouton pour quitter
                    color: "white"
                    font.bold: true
                    font.pixelSize: 16
                    anchors.centerIn: parent
                }
            }
        }
        // ==========================================
        // ÉTAT C : MENU MODIFIER
        // ==========================================
        Column {
            anchors.top: parent.top
            anchors.topMargin: 0
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 25
            visible: root.etatPanneau === "modifier"

            Column {
                spacing: 10
                anchors.horizontalCenter: parent.horizontalCenter
                Text {
                    text: "À quel point je veux boire ce soir ?"
                    color: "white"
                    font.pixelSize: 18
                    font.bold: true
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                Slider {
                    id: sliderSoif
                    width: 350
                    from: 1
                    to: 10
                    value: 5
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }

            Column {
                spacing: 15
                anchors.horizontalCenter: parent.horizontalCenter
                Text {
                    text: "Genre de consommation :"
                    color: "white"
                    font.pixelSize: 18
                    font.bold: true
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Row {
                    spacing: 15
                    anchors.horizontalCenter: parent.horizontalCenter

                    Rectangle {
                        width: 85
                        height: 40
                        radius: 20
                        color: "#fda301"
                        border.color: "white"
                        border.width: 2
                        Text {
                            text: "Bière 🍺"
                            color: "#4d2e00"
                            font.bold: true
                            font.pixelSize: 14
                            anchors.centerIn: parent
                        }
                    }
                    Rectangle {
                        width: 85
                        height: 40
                        radius: 20
                        color: "#4d2e00"
                        Text {
                            text: "Shooter 🥃"
                            color: "white"
                            font.pixelSize: 14
                            anchors.centerIn: parent
                        }
                    }
                    Rectangle {
                        width: 85
                        height: 40
                        radius: 20
                        color: "#4d2e00"
                        Text {
                            text: "Vin 🍷"
                            color: "white"
                            font.pixelSize: 14
                            anchors.centerIn: parent
                        }
                    }
                    Rectangle {
                        width: 85
                        height: 40
                        radius: 20
                        color: "#4d2e00"
                        Text {
                            text: "Drinks 🍹"
                            color: "white"
                            font.pixelSize: 14
                            anchors.centerIn: parent
                        }
                    }
                }
            }

            Row {
                spacing: 30
                anchors.horizontalCenter: parent.horizontalCenter

                Rectangle {
                    id: btnRetour
                    width: 140
                    height: 50
                    radius: 25
                    color: "transparent"
                    border.color: "#fda301"
                    border.width: 2
                    Text {
                        text: "Retour"
                        color: "#fda301"
                        font.bold: true
                        font.pixelSize: 18
                        anchors.centerIn: parent
                    }
                }

                Rectangle {
                    id: btnEnregistrer
                    width: 140
                    height: 50
                    radius: 25
                    color: "#fda301"
                    Text {
                        text: "Enregistrer"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 18
                        anchors.centerIn: parent
                    }
                }
            }
        }
    }
}
