import smbus2
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

class GestionnaireEcrans:
    def __init__(self):
        self.i2c_bus = 3
        self.mux_address = 0x70
        self.oled_address = 0x3C
        
    def changer_canal(self, emplacement):
        """Ouvre la porte du multiplexeur pour le canal demandé."""
        
        # --- L'INVERSION MAGIQUE EST ICI ---
        # Si QML demande 1 -> 6 - 1 = Canal 5
        # Si QML demande 5 -> 6 - 5 = Canal 1
        canal_physique = 6 - emplacement 
        
        valeur = 1 << canal_physique
        try:
            with smbus2.SMBus(self.i2c_bus) as bus:
                bus.write_byte(self.mux_address, valeur)
        except Exception as e:
            print(f"Erreur I2C sur le canal {canal_physique}: {e}")

    def afficher_nom(self, emplacement, nom_joueur):
        """Affiche le nom du joueur sur le petit écran OLED correspondant."""
        self.changer_canal(emplacement)
        
        try:
            serial = i2c(port=self.i2c_bus, address=self.oled_address)
            device = ssd1306(serial)
            
            with canvas(device) as draw:
                draw.text((10, 20), nom_joueur, fill="white")
        except Exception as e:
            print(f"Erreur d'affichage OLED: {e}")