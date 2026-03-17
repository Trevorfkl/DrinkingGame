import time
import math
import random
from luma.core.render import canvas

# --- SETTINGS ---
SCREEN_ORDER = [5, 4, 3, 2, 1]
ORIENTATION = 1      
FILL_SPEED = 5.0     # Faster speed = smoother look on Lite
SCREEN_DELAY = 0.001 # Minimal delay

class BigBubble:
    def __init__(self, total_width):
        self.total_width = total_width
        self.reset()
    def reset(self):
        self.x = random.randint(0, self.total_width)
        self.y = random.randint(4, 28)
        self.size = random.randint(3, 7) 
        self.speed = random.uniform(2.0, 4.5)
    def move(self):
        self.x += self.speed * ORIENTATION
        if self.x < -20 or self.x > self.total_width + 20:
            self.reset()
            self.x = 0 if ORIENTATION == 1 else self.total_width

def run(mux, screens):
    num_screens = len(SCREEN_ORDER)
    total_width = 128 * num_screens
    global_x = 0
    bubbles = [BigBubble(total_width) for _ in range(20)] # Fewer bubbles = higher FPS
    screen_map = {channel: device for device, channel in screens}

    while True:
        # 1. Update Position
        global_x += FILL_SPEED
        if global_x > total_width + 50: global_x = 0
        
        for b in bubbles: b.move()

        # 2. Sequential Draw
        for i, ch in enumerate(SCREEN_ORDER):
            if ch not in screen_map: continue
            
            mux.select_channel(ch)
            device = screen_map[ch]
            start_x = i * 128
            
            with canvas(device) as draw:
                # Optimized: Draw the liquid as one solid block
                if global_x > start_x:
                    fill_w = min(128, int(global_x - start_x))
                    
                    # Wavy top line (Simpler math for Lite OS)
                    slosh = int(math.sin(time.time() * 5 + i) * 5)
                    
                    if ORIENTATION == 1:
                        draw.rectangle((0, 0, fill_w + slosh, 32), fill="white")
                    else:
                        draw.rectangle((128 - (fill_w + slosh), 0, 128, 32), fill="white")

                    # Draw Bubbles
                    for b in bubbles:
                        local_bx = int(b.x - start_x)
                        if 0 <= local_bx <= 128 and local_bx < fill_w:
                            draw.ellipse((local_bx, b.y, local_bx + b.size, b.y + b.size), fill="black")
            
            time.sleep(SCREEN_DELAY)