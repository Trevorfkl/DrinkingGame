import time
import random
from luma.core.render import canvas

# --- PERFORMANCE TUNING ---
# L'écran 1 est en bas (index 0, canal 5), l'écran 5 est en haut (index 4, canal 1)
SCREEN_ORDER = [5, 4, 3, 2, 1]
ORIENTATION = 1      
FILL_SPEED = 6.0     
SCREEN_DELAY = 0.0005 
BUBBLE_COUNT = 15 

class BigBubble:
    def __init__(self, total_width):
        self.total_width = total_width
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.total_width)
        self.y = random.randint(2, 30)
        self.size = random.randint(3, 6) 
        self.speed = random.uniform(3.0, 6.0) * ORIENTATION

    def move(self):
        self.x += self.speed
        if self.x < -20 or self.x > self.total_width + 20:
            self.reset()
            self.x = 0 if ORIENTATION == 1 else self.total_width

# --- CHARGEMENT VERTICAL (TOUR 32x640) ---
HAUTEUR_TOTALE = 128 * len(SCREEN_ORDER) # 640 pixels

# [position_axe_128 (hauteur), position_axe_32 (largeur)]
positions_bulles_chargement = [[random.randint(0, HAUTEUR_TOTALE), random.randint(2, 30)] for _ in range(25)]

def run_chargement(mux, screens, progression):
    """ Fait monter le liquide sur la tour géante de 640px de haut. """
    global positions_bulles_chargement
    
    screen_map = {channel: device for device, channel in screens}
    
    # Calcul de la hauteur globale du liquide (0 à 640 pixels)
    hauteur_totale_liquide = int((progression / 100.0) * HAUTEUR_TOTALE)

    # 1. Animation de la position des bulles sur la tour complète
    for i in range(len(positions_bulles_chargement)):
        positions_bulles_chargement[i][0] += 4 # Vitesse de montée
        if positions_bulles_chargement[i][0] > HAUTEUR_TOTALE: 
            positions_bulles_chargement[i][0] = 0
            positions_bulles_chargement[i][1] = random.randint(2, 30)

    # 2. Dessin écran par écran (du bas vers le haut de la tour)
    for i, ch in enumerate(SCREEN_ORDER):
        if ch not in screen_map: continue
        
        mux.select_channel(ch)
        device = screen_map[ch]
        
        # Combien de pixels de liquide appartiennent à cette tranche de 128px ?
        pixels_liquide = hauteur_totale_liquide - (i * 128)
        pixels_liquide = max(0, min(128, pixels_liquide)) # Limiter entre 0 et 128
        
        with canvas(device) as draw:
            # --- LE LIQUIDE ---
            if pixels_liquide > 0:
                if ORIENTATION == 1:
                    # Le liquide monte de x=0 vers x=128
                    draw.rectangle((0, 0, pixels_liquide, 32), fill="white")
                else:
                    # Le liquide monte de x=128 vers x=0
                    draw.rectangle((128 - pixels_liquide, 0, 128, 32), fill="white")
                
            # --- LES BULLES ---
            for bx_global, by in positions_bulles_chargement:
                bx_local = bx_global - (i * 128)
                
                # Si la bulle est actuellement dans cet écran :
                if 0 <= bx_local < 128:
                    # On vérifie si elle est "sous l'eau" (dans la zone blanche) ou non
                    if ORIENTATION == 1:
                        dans_liquide = bx_local < pixels_liquide
                    else:
                        dans_liquide = bx_local > (128 - pixels_liquide)
                        
                    # Bulle noire dans le liquide blanc, blanche dans l'espace vide
                    couleur = "black" if dans_liquide else "white"
                    draw.rectangle((bx_local, by, bx_local+2, by+2), fill=couleur)
                    
    time.sleep(SCREEN_DELAY)

# ... Le reste du fichier (fonction run) reste inchangé ! ...