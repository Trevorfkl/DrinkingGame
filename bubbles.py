import time
import math
import random
from luma.core.render import canvas

# --- CONTROL PANEL ---
SCREEN_ORDER = [5, 4, 3, 2, 1] 
ORIENTATION = 1      
UNFILL_MODE = False  
SCREEN_DELAY = 0.001 # Reduced to keep it snappy

# --- FLUID CONTROLS ---
FILL_SPEED = 4.0     # Faster fill avoids "jitter"
WAVE_AMPLITUDE = 8   
WAVE_SPEED = 0.5     

class BigBubble:
    def __init__(self, total_width):
        self.total_width = total_width
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.total_width)
        self.y = random.randint(5, 27)
        self.size = random.randint(3, 6) # Big bubbles
        self.speed_x = random.uniform(2.0, 5.0) * ORIENTATION

    def move(self):
        self.x += self.speed_x
        if self.x < -30 or self.x > self.total_width + 30:
            self.reset()
            self.x = 0 if ORIENTATION == 1 else self.total_width

def run(mux, screens):
    num_screens = len(SCREEN_ORDER)
    total_width = 128 * num_screens
    global_liquid_x = 0 if not UNFILL_MODE else total_width
    bubbles = [BigBubble(total_width) for _ in range(25)] # Fewer bubbles = less flicker
    
    wave_timer = 0
    screen_map = {channel: device for device, channel in screens}

    while True:
        # 1. Update progression
        if not UNFILL_MODE:
            if global_liquid_x < total_width: global_liquid_x += FILL_SPEED
            else: time.sleep(1.0); global_liquid_x = 0 
        else:
            if global_liquid_x > 0: global_liquid_x -= FILL_SPEED
            else: time.sleep(1.0); global_liquid_x = total_width

        wave_timer += WAVE_SPEED
        for b in bubbles:
            b.move()

        # 2. Draw to Screens
        for i, physical_channel in enumerate(SCREEN_ORDER):
            if physical_channel not in screen_map: continue
            
            device = screen_map[physical_channel]
            mux.select_channel(physical_channel)
            
            screen_start_x = i * 128
            
            # OPTIMIZED DRAWING: 
            # Instead of a complex wave, we use a single offset per screen
            # to prevent I2C lag.
            with canvas(device) as draw:
                local_wave = int(math.sin(wave_timer + i) * WAVE_AMPLITUDE)
                current_fill = int(global_liquid_x - screen_start_x + local_wave)
                
                if current_fill > 0:
                    fill_width = min(128, current_fill)
                    if ORIENTATION == 1:
                        draw.rectangle((0, 0, fill_width, 32), outline="white", fill="white")
                    else:
                        draw.rectangle((128 - fill_width, 0, 128, 32), outline="white", fill="white")

                    # Draw Bubbles (Only if screen has liquid)
                    for b in bubbles:
                        local_bx = int(b.x - screen_start_x)
                        if 0 <= local_bx <= 128 and local_bx < fill_width:
                            draw.ellipse((local_bx, b.y, local_bx + b.size, b.y + b.size), outline="black", fill="black")

            time.sleep(SCREEN_DELAY)