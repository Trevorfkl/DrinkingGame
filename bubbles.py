import time
import random
from luma.core.render import canvas

# --- PERFORMANCE TUNING ---
SCREEN_ORDER = [5, 4, 3, 2, 1]
ORIENTATION = 1      
FILL_SPEED = 6.0     # Higher = More fluid movement
SCREEN_DELAY = 0.0005 # Minimal delay for high FPS

# Reduce bubble count to keep I2C bus clear
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

# --- NOUVELLES VARIABLES POUR LE CHARGEMENT ---
# On crée des bulles statiques qui montent (X aléatoire sur un seul écran, Y de 0 à 32)
positions_bulles_chargement = [[random.randint(0, 128), random.randint(0, 32)] for _ in range(15)]

def run_chargement(mux, screens, progression):
    """ Dessine une 'frame' du chargement vertical (liquide qui monte) sur tous les écrans. """
    global positions_bulles_chargement
    
    screen_map = {channel: device for device, channel in screens}
    
    # Calcul de la hauteur selon la barre QML (0 à 100%)
    hauteur_liquide = int((progression / 100.0) * 32)
    y_debut_liquide = 32 - hauteur_liquide

    # Animation de montée pour ces bulles spécifiques
    for i in range(len(positions_bulles_chargement)):
        positions_bulles_chargement[i][1] -= 2 # Vitesse de montée
        if positions_bulles_chargement[i][1] < 0: # Si la bulle sort en haut, on la remet en bas
            positions_bulles_chargement[i][0] = random.randint(0, 128)
            positions_bulles_chargement[i][1] = 32

    for ch in SCREEN_ORDER:
        if ch not in screen_map: continue
        
        mux.select_channel(ch)
        device = screen_map[ch]
        
        with canvas(device) as draw:
            # 1. Dessiner le niveau du liquide
            if hauteur_liquide > 0:
                draw.rectangle((0, y_debut_liquide, 128, 32), fill="white")
                
            # 2. Dessiner les bulles ultra-rapides (carrées, selon ta technique d'optimisation !)
            for bx, by in positions_bulles_chargement:
                couleur = "black" if by >= y_debut_liquide else "white"
                draw.rectangle((bx, by, bx+2, by+2), fill=couleur)
                
    time.sleep(SCREEN_DELAY)


def run(mux, screens, worker=None):
    num_screens = len(SCREEN_ORDER)
    total_width = 128 * num_screens
    global_x = 0
    bubbles = [BigBubble(total_width) for _ in range(BUBBLE_COUNT)]
    screen_map = {channel: device for device, channel in screens}

    # LA CORRECTION : La boucle vérifie l'état du Thread en arrière-plan
    while worker is None or (worker.running and worker.mode == "bulles"):
        # 1. Update Global Position
        global_x += FILL_SPEED
        if global_x > total_width + 100:
            global_x = 0
        
        for b in bubbles:
            b.move()

        # 2. Sequential Draw (The "Lean" Loop)
        for i, ch in enumerate(SCREEN_ORDER):
            if ch not in screen_map: continue
            
            mux.select_channel(ch)
            device = screen_map[ch]
            start_x = i * 128
            
            # Local fill logic
            relative_fill = global_x - start_x
            
            if relative_fill > -20: # Start drawing slightly before it hits the screen
                with canvas(device) as draw:
                    # SIMPLIFIED LIQUID: One solid block with a random jitter at the edge
                    jitter = random.randint(-4, 4)
                    fill_w = min(128, int(max(0, relative_fill + jitter)))
                    
                    if fill_w > 0:
                        if ORIENTATION == 1:
                            draw.rectangle((0, 0, fill_w, 32), fill="white")
                        else:
                            draw.rectangle((128 - fill_w, 0, 128, 32), fill="white")

                        # Draw Bubbles (Only the ones on this screen)
                        for b in bubbles:
                            local_bx = int(b.x - start_x)
                            if 0 <= local_bx <= 128 and local_bx < fill_w:
                                draw.rectangle((local_bx, b.y, local_bx + b.size, b.y + b.size), fill="black")
        
        # Ultra-low delay to prevent I2C bus from hanging
        time.sleep(SCREEN_DELAY)