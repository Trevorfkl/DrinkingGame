import smbus2
import time
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

# Utilise 3 ou 1 selon ton bus (celui qui a fait allumer l'écran tout à l'heure)
BUS_I2C = 3  
MUX_ADDRESS = 0x70

# Tes canaux physiques (selon ton câblage inversé ou direct)
# Rappelle-toi : ton test précédent a allumé le canal 5 physique quand tu as ouvert le 1.
CANAUX = [5, 4, 3, 2, 1] 

print("--- DÉBUT DU TEST DES 5 ÉCRANS ---")

bus = smbus2.SMBus(BUS_I2C)
serial = i2c(port=BUS_I2C, address=0x3C)

for i, canal in enumerate(CANAUX):
    try:
        # 1. Ouvrir la porte du multiplexeur pour ce canal
        bus.write_byte(MUX_ADDRESS, 1 << canal)
        time.sleep(0.05)
        
        # 2. Initialiser et dessiner sur l'écran
        device = ssd1306(serial)
        with canvas(device) as draw:
            # On écrit le numéro de l'écran pour les identifier
            draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((10, 10), f"ECRAN {i+1}", fill="white")
            
        print(f"-> Écran sur le canal physique {canal} allumé avec succès !")
    except Exception as e:
        print(f"-> Erreur sur le canal {canal} : {e}")

print("--- FIN DU TEST : Restent allumés 10 secondes ---")
time.sleep(10)