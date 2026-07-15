

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick
import QtQuick.Controls
import EcranJeux
import QtQuick.Particles

// Remplacement des imports 3D par le module 2D
Rectangle {
    id: rectangle
    width: 720
    height: 1280

    gradient: Gradient {
        orientation: Gradient.Horizontal // Modifié pour un effet liquide de haut en bas

        GradientStop {
            position: 0
            color: "#fda301"
        }
        GradientStop {
            position: 0.15351
            color: "#fabd16"
        }
        GradientStop {
            position: 0.46053
            color: "#fedd14"
        }
        GradientStop {
            position: 0.55702
            color: "#fedd14"
        }
        GradientStop {
            position: 0.81579
            color: "#fabd16"
        }
        GradientStop {
            position: 1
            color: "#fda301"
        }
    }

    // --- DÉBUT DU SYSTÈME DE BULLES ---
    ParticleSystem {
        id: bubbleSystem
    }

    ItemParticle {
        id: bubbleParticle
        system: bubbleSystem

        delegate: Rectangle {
            width: 20
            height: 20
            radius: 10 // La moitié de la largeur/hauteur = un cercle parfait !

            color: "transparent" // L'intérieur de la bulle
            border.color: "white" // Le contour de la bulle
            border.width: 1
            opacity: 0.6 // Semi-transparent pour voir la bière au travers

            // Petit bonus : un mini reflet pour donner un effet 3D à la bulle
            Rectangle {
                width: 5
                height: 5
                radius: 2.5
                color: "white"
                x: 4
                y: 4
                opacity: 0.8
            }
        }
    }

    Emitter {
        id: bubbleEmitter
        system: bubbleSystem
        anchors.bottom: parent.bottom
        width: parent.width
        height: 10
        emitRate: 20
        lifeSpan: 6000 // Les bulles vivent 6 secondes (le temps de monter)
        lifeSpanVariation: 1000
        size: 10
        sizeVariation: 5
        endSize: 20 // Elles grossissent en remontant
        velocity: PointDirection {
            y: -250 // Vitesse vers le haut
            yVariation: 40
            xVariation: 15
        }
    }

    Wander {
        id: bubbleWander
        system: bubbleSystem
        anchors.fill: parent
        affectedParameter: Wander.Position
        xVariance: 30
        pace: 120
    }

    // --- FIN DU SYSTÈME DE BULLES ---
    Item {
        id: __materialLibrary__
    }

    states: [
        State {
            name: "clicked"
        }
    ]
}
