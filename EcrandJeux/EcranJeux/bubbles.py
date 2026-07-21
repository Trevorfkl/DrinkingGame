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

def run(mux, screens):
    num_screens = len(SCREEN_ORDER)
    total_width = 128 * num_screens
    global_x = 0
    bubbles = [BigBubble(total_width) for _ in range(BUBBLE_COUNT)]
    screen_map = {channel: device for device, channel in screens}

    while True:
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
                    # This is much faster than math.sin()
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
                                # Use rectangle instead of ellipse for faster rendering
                                draw.rectangle((local_bx, b.y, local_bx + b.size, b.y + b.size), fill="black")
            
            # Ultra-low delay to prevent I2C bus from hanging
            time.sleep(SCREEN_DELAY)