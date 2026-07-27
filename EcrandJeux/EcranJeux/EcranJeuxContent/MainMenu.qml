import QtQuick
import QtQuick.Controls

MainMenuForm {
    id: interfaceVisuelle

    // On déclare les signaux pour Python
    signal joueurSelectionne(string nom)
    signal nouveauJoueurCree(string nom)
    signal joueurCedePlace(string nom)
    signal quit

    // ========================================================
    // AJOUT 1 : Détecter quand le carrousel tourne
    // ========================================================
    onIndexCarrouselChanged: {
        console.log("🔄 [QML] Le carrousel tourne (Index actuel: " + interfaceVisuelle.indexCarrousel + ")")
        // On ramène le menu à la base (ferme les options)
        interfaceVisuelle.etatPanneau = "base"

        // On vérifie si la nouvelle place est occupée ou libre, et on met à jour l'interrupteur
        if (interfaceVisuelle.carrouselModel.count > 0) {
            let occupe = interfaceVisuelle.carrouselModel.get(interfaceVisuelle.indexCarrousel).hasPlayer
            interfaceVisuelle.placeActuelleOccupee = occupe
        }
    }

    // 1. Clic sur "SÉLECTIONNER" (Joueur existant)
    MouseArea {
        parent: interfaceVisuelle.clicSelectionner
        anchors.fill: parent
        onClicked: {
            interfaceVisuelle.etatPanneau = "options"

            if (interfaceVisuelle.carrouselModel.count > 0) {
                let nomActuel = interfaceVisuelle.carrouselModel.get(interfaceVisuelle.indexCarrousel).playerName
                console.log("🖱️ [QML] Clic sur SÉLECTIONNER pour le joueur : " + nomActuel)
                backend_python.joueurSelectionne(nomActuel)
            }
        }
    }

   // 2. Clic sur "AJOUTER" (Anciennement CRÉER)
        MouseArea {
            parent: interfaceVisuelle.clicCreer
            anchors.fill: parent
            onClicked: {
                let nomEntre = interfaceVisuelle.texteChampNom

                if(nomEntre !== "") {
                    let indexActuel = interfaceVisuelle.indexCarrousel
                    console.log("🖱️ [QML] Clic sur AJOUTER pour '" + nomEntre + "' à l'emplacement " + (indexActuel + 1))

                    // 1. On demande à Python les stats
                    let reponseTexte = backend_python.chargerOuCreerJoueur(nomEntre)
                    let stats = JSON.parse(reponseTexte)

                    // 3. On met à jour la carte visuelle
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "hasPlayer", true)
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "playerName", nomEntre)
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "coins", stats.coins)
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "gorgees", stats.gorgees)

                    // 🚀 LA CONNEXION AVEC LES ÉCRANS OLED
                    backend_python.nouveau_joueur_ajoute(indexActuel + 1, nomEntre)

                    interfaceVisuelle.placeActuelleOccupee = true
                    interfaceVisuelle.etatPanneau = "modifier"
                }
            }
        }

    // 3. Clic sur "Modifier"
    MouseArea {
        parent: interfaceVisuelle.clicModifier
        anchors.fill: parent
        onClicked: {
            console.log("🖱️ [QML] Clic sur MODIFIER")
            interfaceVisuelle.etatPanneau = "modifier"
        }
    }

    // 4. Clic sur "Retour"
    MouseArea {
        parent: interfaceVisuelle.clicRetour
        anchors.fill: parent
        onClicked: {
            interfaceVisuelle.etatPanneau = "options"
        }
    }

    // 5. Clic sur "Enregistrer"
    MouseArea {
            parent: interfaceVisuelle.clicEnregistrer
            anchors.fill: parent
            onClicked: {
                let indexActuel = interfaceVisuelle.indexCarrousel
                let vraiNom = interfaceVisuelle.carrouselModel.get(indexActuel).playerName
                let vraiesCoins = interfaceVisuelle.carrouselModel.get(indexActuel).coins
                let vraiesGorgees = interfaceVisuelle.carrouselModel.get(indexActuel).gorgees

                console.log("🖱️ [QML] Clic sur ENREGISTRER. Sauvegarde demandée pour " + vraiNom)
                backend_python.enregistrerStats(vraiNom, vraiesCoins, vraiesGorgees)
                interfaceVisuelle.etatPanneau = "options"
            }
        }

    // 6. Clic sur "Pu Capable 🤮" (Céder sa place)
        MouseArea {
            parent: interfaceVisuelle.clicPoubelle
            anchors.fill: parent
            onClicked: {
                let indexActuel = interfaceVisuelle.indexCarrousel
                let vraiNom = interfaceVisuelle.carrouselModel.get(indexActuel).playerName
                
                console.log("🗑️ [QML] Clic sur POUBELLE. Éjection du joueur : " + vraiNom)

                backend_python.joueurCedePlace(vraiNom)

                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "hasPlayer", false)
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "playerName", "")
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "coins", 0)
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "gorgees", 0)

                interfaceVisuelle.placeActuelleOccupee = false
                interfaceVisuelle.etatPanneau = "base"
            }
        }

    // ==========================================
    // BOUTON "AJOUTER UNE PLACE" (Max 5)
    // ==========================================
    Rectangle {
        id: btnAjouterPlace
        width: texteBouton.contentWidth + 50
        height: 50
        radius: 25
        color: "#2ecc71" // Un beau vert

        anchors.bottom: parent.bottom
        anchors.bottomMargin: 30
        anchors.horizontalCenter: parent.horizontalCenter

        visible: interfaceVisuelle.carrouselModel.count < 5

        Text {
            id: texteBouton
            text: "➕ Ajouter une place (" + interfaceVisuelle.carrouselModel.count + "/5)"
            color: "white"
            font.bold: true
            font.pixelSize: 18
            anchors.centerIn: parent
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                if (interfaceVisuelle.carrouselModel.count < 5) {
                    interfaceVisuelle.carrouselModel.append({
                        "hasPlayer": false,
                        "playerName": "",
                        "coins": 0,
                        "gorgees": 0
                    })
                    interfaceVisuelle.indexCarrousel = interfaceVisuelle.carrouselModel.count - 1
                }
            }
        }
    }

    // ==========================================
    // NOUVEAU BOUTON : "DÉMARRER LA PARTIE"
    // ==========================================
    Rectangle {
        id: btnDemarrerJeu
        z: 100
        width: 320
        height: 60
        radius: 30
        color: "#f39c12" // Orange doré

        // On l'ancre JUSTE AU-DESSUS du bouton Ajouter
        anchors.bottom: btnAjouterPlace.top
        anchors.bottomMargin: 15
        anchors.horizontalCenter: parent.horizontalCenter

        // Visible uniquement dans le menu de base, et seulement s'il y a au moins 1 joueur actif !
        visible: interfaceVisuelle.etatPanneau === "base" 

        Text {
            text: "🎮 DÉMARRER LA PARTIE"
            color: "white"
            font.bold: true
            font.pixelSize: 20
            anchors.centerIn: parent
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                console.log("🍻 [QML] Clic sur Démarrer. Passage au Lobby.")
                // On passe le modèle des joueurs à la nouvelle page pour générer les sliders !
                stackView.push("ParametresPartie.qml", { "modeleJoueurs": interfaceVisuelle.carrouselModel })
            }
        }
    }

    // ==========================================
    // BOUTON "X ROUGE" (Supprimer l'emplacement vide)
    // ==========================================
    Rectangle {
        id: btnSupprimerPlace
        width: 40
        height: 40
        radius: 20
        color: "#e74c3c"

        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 20

        visible: interfaceVisuelle.etatPanneau === "base" && !interfaceVisuelle.placeActuelleOccupee && interfaceVisuelle.carrouselModel.count > 1

        Text {
            text: "✖"
            color: "white"
            font.bold: true
            font.pixelSize: 20
            anchors.centerIn: parent
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                if (interfaceVisuelle.carrouselModel.count > 1) {
                    interfaceVisuelle.carrouselModel.remove(interfaceVisuelle.indexCarrousel)
                    let occupe = interfaceVisuelle.carrouselModel.get(interfaceVisuelle.indexCarrousel).hasPlayer
                    interfaceVisuelle.placeActuelleOccupee = occupe
                }
            }
        }
    }

    // ==========================================
    // INITIALISATION
    // ==========================================
    Component.onCompleted: {
        console.log("🚀 [QML] Démarrage... Synchronisation des joueurs par défaut avec les OLED.")
        for (let i = 0; i < interfaceVisuelle.carrouselModel.count; i++) {
            let place = interfaceVisuelle.carrouselModel.get(i)
            if (place.hasPlayer && place.playerName !== "") {
                backend_python.nouveau_joueur_ajoute(i + 1, place.playerName)
            }
        }
    }
}