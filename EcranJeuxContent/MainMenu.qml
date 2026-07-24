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
                    // 1. On demande à Python les stats (ça nous revient sous forme de texte JSON)
                    let reponseTexte = backend_python.chargerOuCreerJoueur(nomEntre)

                    // 2. On transforme le texte JSON en vrai objet utilisable
                    let stats = JSON.parse(reponseTexte)

                    // 3. On met à jour la carte visuelle avec les VRAIES stats !
                    let indexActuel = interfaceVisuelle.indexCarrousel
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "hasPlayer", true)
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "playerName", nomEntre)
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "coins", stats.coins)
                    interfaceVisuelle.carrouselModel.setProperty(indexActuel, "gorgees", stats.gorgees)

                    // 4. On indique que la place est prise et on passe aux options
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
                // CORRECTION DE L'ERREUR : On va chercher les vraies informations de la carte actuelle
                let indexActuel = interfaceVisuelle.indexCarrousel
                let vraiNom = interfaceVisuelle.carrouselModel.get(indexActuel).playerName
                let vraiesCoins = interfaceVisuelle.carrouselModel.get(indexActuel).coins
                let vraiesGorgees = interfaceVisuelle.carrouselModel.get(indexActuel).gorgees

                console.log("Sauvegarde demandée pour " + vraiNom)

                // On envoie les vraies variables à Python
                backend_python.enregistrerStats(vraiNom, vraiesCoins, vraiesGorgees)

                // On retourne au menu précédent
                interfaceVisuelle.etatPanneau = "options"
            }
        }

    // 6. Clic sur "Pu Capable 🤮" (Céder sa place)
        MouseArea {
            parent: interfaceVisuelle.clicPoubelle // Vérifie que c'est bien le bon ID pour ton bouton
            anchors.fill: parent
            onClicked: {
                let indexActuel = interfaceVisuelle.indexCarrousel
                let vraiNom = interfaceVisuelle.carrouselModel.get(indexActuel).playerName

                // 1. On avertit Python
                backend_python.joueurCedePlace(vraiNom)

                // 2. On vide complètement la carte actuelle
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "hasPlayer", false)
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "playerName", "")
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "coins", 0)
                interfaceVisuelle.carrouselModel.setProperty(indexActuel, "gorgees", 0)

                // 3. On remet l'interrupteur à "vide" et on retourne au menu de base
                interfaceVisuelle.placeActuelleOccupee = false
                interfaceVisuelle.etatPanneau = "base"
            }
        }
    // ==========================================
        // BOUTON "AJOUTER UNE PLACE" (Max 5)
        // ==========================================
        Rectangle {
            id: btnAjouterPlace
            width: 250
            height: 50
            radius: 25
            color: "#2ecc71" // Un beau vert

            // On le place en bas, au centre
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 30
            anchors.horizontalCenter: parent.horizontalCenter

            // Le bouton DISPARAÎT si on a 5 places ou plus !
            visible: interfaceVisuelle.carrouselModel.count < 5

            Text {
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
                        // On ajoute une carte vide au carrousel
                        interfaceVisuelle.carrouselModel.append({
                            "hasPlayer": false,
                            "playerName": "",
                            "coins": 0,
                            "gorgees": 0
                        })

                        // On fait défiler le carrousel jusqu'à cette nouvelle place
                        interfaceVisuelle.indexCarrousel = interfaceVisuelle.carrouselModel.count - 1
                    }
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
                radius: 20 // Pour faire un cercle parfait
                color: "#e74c3c" // Un beau rouge

                // On le place en haut à droite
                anchors.top: parent.top
                anchors.topMargin: 20
                anchors.right: parent.right
                anchors.rightMargin: 20

                // VISIBLE SEULEMENT SI : On est dans le menu de base + la place est vide + il y a plus d'une carte
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
                            // On supprime la carte actuelle du carrousel
                            interfaceVisuelle.carrouselModel.remove(interfaceVisuelle.indexCarrousel)

                            // On met à jour l'interrupteur avec la nouvelle carte qui prend sa place
                            let occupe = interfaceVisuelle.carrouselModel.get(interfaceVisuelle.indexCarrousel).hasPlayer
                            interfaceVisuelle.placeActuelleOccupee = occupe
                        }
                    }
                }
            }
}
