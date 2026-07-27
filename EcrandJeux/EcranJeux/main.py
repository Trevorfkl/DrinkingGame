import sys
import os
import json
import time
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QThread

import rc_EcranJeux

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
os.environ["QML2_IMPORT_PATH"] = PROJECT_PATH

# ==========================================
# 1. GESTION DU MATÉRIEL 
# ==========================================
try:
    import smbus2
    from luma.oled.device import ssd1306
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas  
    import bubbles 
    HARDWARE_ACTIF = True
    print("[PYTHON] Mode Raspberry Pi activé. Modules matériels chargés.")
except ImportError as e:
    HARDWARE_ACTIF = False
    print(f"[ATTENTION] Erreur import : {e}")
    print("[ATTENTION] Mode simulation PC activé.")

if HARDWARE_ACTIF:
    class TCA9548A:
        def __init__(self, bus, address=0x70):
            self.bus = bus
            self.address = address

        def select_channel(self, channel):
            if 0 <= channel <= 7:
                self.bus.write_byte(self.address, 1 << channel)

# ==========================================
# 2. LE THREAD MATÉRIEL (Connecté à bubbles.py)
# ==========================================
class ScreenWorker(QThread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.mode = "chargement" 
        self.progression = 0
        self.derniere_progression = -1 
        self.bus_i2c = 3
        self.mux_address = 0x70
        self.canaux = [5, 4, 3, 2, 1] 
        self.bus = None
        self.serial = None
        self.mux = None
        self.ecrans_actifs = [] 
        
        # 🚀 NOUVEAU : Une mémoire interne pour les places !
        self.joueurs_presents = {1: None, 2: None, 3: None, 4: None, 5: None}

    def run(self):
        if not HARDWARE_ACTIF:
            while self.running:
                self.msleep(100)
            return

        print("[OLED] Démarrage du moteur d'animation...")
        try:
            self.bus = smbus2.SMBus(self.bus_i2c)
            self.serial = i2c(port=self.bus_i2c, address=0x3C)
            self.mux = TCA9548A(self.bus, self.mux_address)
            
            # 1. Initialisation unique des écrans
            for canal in self.canaux:
                self.mux.select_channel(canal)
                time.sleep(0.05)
                # 🚀 CORRECTION 1 : On force la taille de l'écran à 128x32 !
                device = ssd1306(self.serial, width=128, height=32)
                self.ecrans_actifs.append((device, canal))
            
            # 2. Boucle d'animation connectée à tes bulles
            while self.running:
                if self.mode == "chargement":
                    if self.progression != self.derniere_progression:
                        bubbles.run_chargement(self.mux, self.ecrans_actifs, self.progression)
                        self.derniere_progression = self.progression
                        
                    # 🚀 CORRECTION 2 : On attend d'avoir affiché le 100% avant de changer
                    if self.progression >= 100:
                        self.msleep(800) # On laisse la tour pleine s'afficher 0.8 seconde
                        self.mode = "transition_attente"
                        
                elif self.mode == "transition_attente":
                    self.afficher_ecrans_attente()
                    self.mode = "attente"
                    
                self.msleep(10) 
                
        except Exception as e:
            print(f"[OLED] Erreur matérielle dans la boucle : {e}")

    def afficher_ecrans_attente(self):
        if not self.bus: return
        for i, (device, canal) in enumerate(self.ecrans_actifs):
            emplacement = i + 1
            nom_sauvegarde = self.joueurs_presents[emplacement] # On consulte la mémoire
            
            try:
                self.mux.select_channel(canal)
                with canvas(device) as draw:
                    draw.rectangle(device.bounding_box, outline="white", fill="black")
                    draw.text((35, 6), f"JOUEUR {emplacement}", fill="white")
                    
                    if nom_sauvegarde:
                        # La place est prise, on remet le nom !
                        draw.text((10, 20), f"> {nom_sauvegarde[:15]}", fill="white")
                    else:
                        # La place est vide
                        draw.text((25, 20), "EN ATTENTE...", fill="white")
            except Exception:
                pass

    def afficher_nom_joueur(self, emplacement, nom):
        if not HARDWARE_ACTIF or not self.bus:
            return
        if 1 <= emplacement <= 5:
            # 🚀 NOUVEAU : On mémorise le joueur dans le dictionnaire
            self.joueurs_presents[emplacement] = nom
            
            canal_physique = self.canaux[emplacement - 1]
            for device, canal in self.ecrans_actifs:
                if canal == canal_physique:
                    try:
                        self.mux.select_channel(canal)
                        with canvas(device) as draw:
                            draw.rectangle(device.bounding_box, outline="white", fill="black")
                            draw.text((35, 6), f"JOUEUR {emplacement}", fill="white")
                            draw.text((10, 20), f"> {nom[:15]}", fill="white") 
                    except Exception as e:
                        print(f"Erreur affichage {canal_physique}: {e}")

    def arreter(self):
        self.running = False
        if self.bus:
            try:
                self.bus.write_byte(self.mux_address, 0)
                self.bus.close()
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
            print("📁 [PYTHON] Création d'un nouveau fichier de sauvegarde (sauvegarde.json).")
        else:
            print(f"📁 [PYTHON] Sauvegarde chargée avec {len(self.joueurs_data)} joueurs existants.")

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
        print(f"🔍 [PYTHON] QML demande le profil de : '{nom}'")
        if nom in self.joueurs_data:
            print(f"   -> Profil existant trouvé pour {nom}.")
            return json.dumps(self.joueurs_data[nom])
        else:
            print(f"   -> Nouveau profil créé pour {nom}.")
            nouveau_profil = {"coins": 0, "gorgees": 0}
            self.joueurs_data[nom] = nouveau_profil
            self.sauvegarder_donnees()
            return json.dumps(nouveau_profil)

    @Slot(int)
    def majProgressionChargement(self, valeur):
        self.worker.progression = valeur

    @Slot(str, int, int)
    def enregistrerStats(self, nom, nouveau_coins, nouvelles_gorgees):
        print(f"💾 [PYTHON] Sauvegarde des stats pour {nom} | Coins: {nouveau_coins} | Gorgées: {nouvelles_gorgees}")
        if nom in self.joueurs_data:
            self.joueurs_data[nom]["coins"] = nouveau_coins
            self.joueurs_data[nom]["gorgees"] = nouvelles_gorgees
        else:
            self.joueurs_data[nom] = {"coins": nouveau_coins, "gorgees": nouvelles_gorgees}
        self.sauvegarder_donnees()
        
    @Slot(str)
    def joueurSelectionne(self, nom): 
        print(f"🎯 [PYTHON] Joueur existant sélectionné : {nom}")

    @Slot(str)
    def joueurCedePlace(self, nom): 
        print(f"🗑️ [PYTHON] Le joueur {nom} vient de céder sa place (Bouton Poubelle).")
        # Note : On pourra ajouter le code ici plus tard pour remettre l'écran à "EN ATTENTE..."
        
    @Slot(int, str)
    def nouveau_joueur_ajoute(self, emplacement, nom):
        print(f"✨ [PYTHON] Ajout de '{nom}' sur l'écran physique numéro {emplacement}.")
        self.worker.afficher_nom_joueur(emplacement, nom)
# ==========================================
# LANCEMENT
# ==========================================
if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    worker = ScreenWorker()
    worker.start()

    backend = Backend(worker)
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