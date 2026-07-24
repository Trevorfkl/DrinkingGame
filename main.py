import sys
import os
import json
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QThread

# 1. On importe le fichier de ressources
import rc_EcranJeux
from ecrans_joueurs import GestionnaireEcrans

# 2. On rend le chemin dynamique
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
os.environ["QML2_IMPORT_PATH"] = PROJECT_PATH

# ==========================================
# 1. GESTION DU MATÉRIEL (Bouclier PC/Raspberry Pi)
# ==========================================
try:
    from smbus2 import SMBus
    from luma.oled.device import ssd1306
    from luma.core.interface.serial import i2c
    import bubbles
    import animations
    HARDWARE_ACTIF = True
    print("[PYTHON] Mode Raspberry Pi activé. Modules matériels chargés.")
except ImportError:
    HARDWARE_ACTIF = False
    print("[ATTENTION] Modules matériels absents (smbus2, luma). Mode simulation PC activé.")

if HARDWARE_ACTIF:
    class TCA9548A:
        def __init__(self, bus, address=0x70):
            self.bus = bus
            self.address = address

        def select_channel(self, channel):
            if 0 <= channel <= 7:
                self.bus.write_byte(self.address, 1 << channel)

    def init_hardware():
        print("Initialisation des canaux 1 à 5...")
        # ⚠️ ATTENTION : Vérifie bien ton bus I2C ici. 
        # On avait configuré le bus 3 (SMBus(3)) plus tôt pour esquiver le bouton Kano.
        bus = SMBus(3) 
        mux = TCA9548A(bus)
        screens = []
        
        for ch in range(1, 6):
            mux.select_channel(ch)
            try:
                serial = i2c(port=3, address=0x3C)
                device = ssd1306(serial, width=128, height=32)
                screens.append((device, ch))
            except Exception as e:
                print(f"Erreur sur le canal {ch}: {e}")
                
        return mux, screens

# ==========================================
# 2. LE MOTEUR D'ANIMATION EN ARRIÈRE-PLAN
# ==========================================
class ScreenWorker(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.mode = "chargement" 
        self.progression = 0     
        self.mux = None
        self.screens = []

    def run(self):
        if HARDWARE_ACTIF:
            self.mux, self.screens = init_hardware()
            print("--- Cerveau matériel initialisé ---")
            
            while self.running:
                if self.mode == "chargement":
                    bubbles.run_chargement(self.mux, self.screens, self.progression)
                elif self.mode == "bulles":
                    bubbles.run(self.mux, self.screens, worker=self)
                elif self.mode == "victory":
                    animations.play_animation(self.mux, self.screens, "victory")
        else:
            while self.running:
                self.msleep(100)

    # 🚀 AJOUTE CETTE MÉTHODE ICI :
    def afficher_nom_joueur(self, emplacement, nom):
        """Permet d'afficher un nom sur un écran spécifique sans casser le thread"""
        if not HARDWARE_ACTIF or not self.mux:
            return
        
        # Applique ton inversion de canal (ex: 1 devient 5)
        canal_physique = 6 - emplacement
        
        for device, ch in self.screens:
            if ch == canal_physique:
                try:
                    self.mux.select_channel(canal_physique)
                    from luma.core.render import canvas
                    with canvas(device) as draw:
                        draw.rectangle(device.bounding_box, outline="white", fill="black")
                        draw.text((2, 10), nom[:16], fill="white") # Tronque si trop long pour 128x32
                except Exception as e:
                    print(f"Erreur affichage joueur écran {canal_physique}: {e}")

    def arreter(self):
        self.running = False
        if HARDWARE_ACTIF and self.mux:
            try:
                self.mux.bus.write_byte(0x70, 0)
            except:
                pass

# ==========================================
# 3. LE CERVEAU PYTHON (Backend QML)
# ==========================================
class Backend(QObject):
    @Slot(str, result=str)
    def chargerOuCreerJoueur(self, nom): 
        if nom in self.joueurs_data:
            return json.dumps(self.joueurs_data[nom])
        else:
            nouveau_profil = {"coins": 0, "gorgees": 0}
            self.joueurs_data[nom] = nouveau_profil
            self.sauvegarder_donnees()
            return json.dumps(nouveau_profil)

    # ----------------------------------------------------
    @Slot(int)
    def majProgressionChargement(self, valeur):
        print(f"--- QML envoie la progression : {valeur}% ---") 
        
        self.worker.progression = valeur
        
        if valeur >= 100:
            self.worker.mode = "bulles"

    # --- LES FONCTIONS QU'IL MANQUAIT SONT ICI ---
    @Slot(str, int, int)
    def enregistrerStats(self, nom, nouveau_coins, nouvelles_gorgees):
        if nom in self.joueurs_data:
            self.joueurs_data[nom]["coins"] = nouveau_coins
            self.joueurs_data[nom]["gorgees"] = nouvelles_gorgees
        else:
            self.joueurs_data[nom] = {"coins": nouveau_coins, "gorgees": nouvelles_gorgees}
        self.sauvegarder_donnees()
        
    @Slot(str)
    def joueurSelectionne(self, nom): 
        print(f"[PYTHON] Sélection : {nom}")

    @Slot(str)
    def joueurCedePlace(self, nom): 
        print(f"[PYTHON] Départ : {nom}")
        
    @Slot(int, str)
    def nouveau_joueur_ajoute(self, emplacement, nom):
            print(f"[PYTHON] QML demande : joueur {nom} à l'emplacement {emplacement}")
            # On passe l'ordre directement au worker central
            self.worker.afficher_nom_joueur(emplacement, nom)

    def __init__(self, screen_worker):
        super().__init__()
        self.worker = screen_worker
        
        # Initialisation de la classe de ton nouveau fichier
        self.gestionnaire_ecrans = GestionnaireEcrans()
        
        dossier_actuel = os.path.dirname(os.path.abspath(__file__))
        self.fichier_json = os.path.join(dossier_actuel, "sauvegarde.json")
        self.joueurs_data = self.charger_donnees()
        
        if not os.path.exists(self.fichier_json):
            self.sauvegarder_donnees()

    def charger_donnees(self):
        if os.path.exists(self.fichier_json):
            with open(self.fichier_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def sauvegarder_donnees(self):
        with open(self.fichier_json, 'w', encoding='utf-8') as f:
            json.dump(self.joueurs_data, f, indent=4, ensure_ascii=False)

    @Slot(str, result=str)
    def chargerOuCreerJoueur(self, nom): 
        # ... (ton code JSON intact) ...
        if nom in self.joueurs_data:
            return json.dumps(self.joueurs_data[nom])
        else:
            nouveau_profil = {"coins": 0, "gorgees": 0}
            self.joueurs_data[nom] = nouveau_profil
            self.sauvegarder_donnees()
            return json.dumps(nouveau_profil)

    # --- NOUVEAU SLOT POUR LES ÉCRANS ---
    @Slot(int, str)
    def nouveau_joueur_ajoute(self, emplacement, nom):
        print(f"[PYTHON] QML demande : joueur {nom} à l'emplacement {emplacement}")
        # On envoie l'instruction matérielle
        self.gestionnaire_ecrans.afficher_nom(emplacement, nom)

# ==========================================
# LANCEMENT
# ==========================================
if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Démarrage du thread d'animation
    worker = ScreenWorker()
    worker.start()

    # Démarrage du backend (qui contient maintenant GestionnaireEcrans)
    backend = Backend(worker)
    
    # ⚠️ IMPORTANT: C'est le nom exact que tu dois utiliser dans ton fichier QML
    engine.rootContext().setContextProperty("backend_python", backend)

    engine.addImportPath(PROJECT_PATH)
    engine.addImportPath(os.path.join(PROJECT_PATH, "EcranJeuxContent"))

    app_path = os.path.join(PROJECT_PATH, "EcranJeuxContent/App.qml")
    engine.load(app_path)

    if not engine.rootObjects():
        sys.exit(-1)
        
    code_retour = app.exec()
    
    print("Arrêt du matériel...")
    worker.arreter()
    worker.wait()
    sys.exit(code_retour)