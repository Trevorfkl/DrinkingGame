import sys
import os
import json
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QThread

# 1. On importe le fichier de ressources que tu viens de compiler
import rc_EcranJeux

# 2. On rend le chemin dynamique (trouve le dossier actuel du fichier main.py)
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
        bus = SMBus(1)
        mux = TCA9548A(bus)
        screens = []
        
        for ch in range(1, 6):
            mux.select_channel(ch)
            try:
                serial = i2c(port=1, address=0x3C)
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
        self.mode = "bulles" # Mode par défaut

    def run(self):
        if HARDWARE_ACTIF:
            mux, screens = init_hardware()
            print("--- Cerveau matériel initialisé ---")
            
            # Note: Si bubbles.run contient une boucle "while True", 
            # il faudra la remplacer par "while self.running" dans ton fichier bubbles.py
            while self.running:
                if self.mode == "bulles":
                    bubbles.run(mux, screens)
                elif self.mode == "victory":
                    animations.play_animation(mux, screens, "victory")
        else:
            # Mode PC : On simule l'attente sans rien faire planter
            while self.running:
                self.msleep(100)

    def arreter(self):
        self.running = False
        if HARDWARE_ACTIF:
            try:
                bus = SMBus(1)
                bus.write_byte(0x70, 0)
            except:
                pass

# ==========================================
# 3. LE CERVEAU PYTHON (Backend QML)
# ==========================================
class Backend(QObject):
    def __init__(self, screen_worker):
        super().__init__()
        self.worker = screen_worker
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
        if nom in self.joueurs_data:
            return json.dumps(self.joueurs_data[nom])
        else:
            nouveau_profil = {"coins": 0, "gorgees": 0}
            self.joueurs_data[nom] = nouveau_profil
            self.sauvegarder_donnees()
            return json.dumps(nouveau_profil)

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
        # Note : On ne supprime pas le joueur du fichier JSON pour garder 
        # ses stats pour la prochaine fois, on fait juste le retirer de la table.
        # Exemple d'interaction : Si Trévys ajoute une gorgée, on peut déclencher l'animation
        # self.worker.mode = "shot_pour"

# ==========================================
# LANCEMENT
# ==========================================
if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # On démarre le thread des écrans OLED
    worker = ScreenWorker()
    worker.start()

    engine.addImportPath(PROJECT_PATH)
    engine.addImportPath(os.path.join(PROJECT_PATH, "EcranJeuxContent"))

    backend = Backend(worker)
    engine.rootContext().setContextProperty("backend_python", backend)

    app_path = os.path.join(PROJECT_PATH, "EcranJeuxContent/App.qml")
    engine.load(app_path)

    if not engine.rootObjects():
        sys.exit(-1)
        
    code_retour = app.exec()
    
    # Quand on quitte l'application, on coupe proprement les écrans
    print("Arrêt du matériel...")
    worker.arreter()
    worker.wait()
    sys.exit(code_retour)