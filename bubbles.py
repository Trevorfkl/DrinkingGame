import time
import math
import random
from luma.core.render import canvas

# --- CONTROL PANEL ---
SCREEN_ORDER = [5, 4, 3, 2, 1] 
ORIENTATION = 1      # 1: Left-to-Right, -1: Right-to-Left
UNFILL_MODE = False  # True: Draining mode
SCREEN_DELAY = 0.002 # Delay between hardware signals

# --- NEW FLUID CONTROLS ---
FILL_SPEED = 2.5     # Higher = faster fill
WAVE_AMPLITUDE = 6   # How "tall" the wave is (in pixels)
WAVE_FREQUENCY = 0.1 # How many "bumps" in the wave (lower = smoother)
WAVE_SPEED = 0.4     # How fast the waves "slosh" back and forth

class BigBubble:
    def __init__(self, total_width):
        self.total_width = total_width
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.total_width)
        self.y = random.randint(5, 27)
        self.size = random.randint(2, 5) 
        self.speed_x = random.uniform(1.2, 4.0) * ORIENTATION

    def move(self):
        self.x += self.speed_x
        if self.x < -20 or self.x > self.total_width + 20:
            self.reset()
            self.x = 0 if ORIENTATION == 1 else self.total_width

def run(mux, screens):
    num_screens = len(SCREEN_ORDER)
    total_width = 128 * num_screens
    global_liquid_x = 0 if not UNFILL_MODE else total_width
    bubbles = [BigBubble(total_width) for _ in range(40)]
    
    # Internal timer for wave animation
    wave_offset = 0
    screen_map = {channel: device for device, channel in screens}

    while True:
        # 1. Update Progression
        if not UNFILL_MODE:
            if global_liquid_x < total_width: global_liquid_x += FILL_SPEED
            else: time.sleep(1.5); global_liquid_x = 0 
        else:
            if global_liquid_x > 0: global_liquid_x -= FILL_SPEED
            else: time.sleep(1.5); global_liquid_x = total_width

        # Update Bubbles and Wave slosh
        wave_offset += WAVE_SPEED
        for b in bubbles:
            b.move()

        # 2. Draw to Screens
        for i, physical_channel in enumerate(SCREEN_ORDER):
            if physical_channel not in screen_map: continue
            
            device = screen_map[physical_channel]
            mux.select_channel(physical_channel)
            
            screen_start_x = i * 128
            screen_end_x = screen_start_x + 127
            
            # Draw the fluid
            with canvas(device) as draw:
                # We calculate the "wave" for every column on the screen
                # This makes it look like real liquid moving across the glass
                for local_x in range(0, 128, 4): # Step by 4 for performance
                    global_x = screen_start_x + local_x
                    
                    # Calculate the Sine Wave height at this specific X point
                    slosh = math.sin((global_x * WAVE_FREQUENCY) + wave_offset) * WAVE_AMPLITUDE
                    
                    # Check if liquid has reached this global coordinate
                    if global_liquid_x > (global_x + slosh):
                        # Draw vertical sliver of beer
                        if ORIENTATION == 1:
                            draw.rectangle((0, 0, local_x + 4, 32), outline="white", fill="white")
                        else:
                            draw.rectangle((128 - (local_x + 4), 0, 128, 32), outline="white", fill="white")

                # 3. Draw Bubbles
                for b in bubbles:
                    if screen_start_x <= b.x <= screen_end_x:
                        local_bx = int(b.x - screen_start_x)
                        # Wave height at bubble's X position
                        bubble_slosh = math.sin((b.x * WAVE_FREQUENCY) + wave_offset) * WAVE_AMPLITUDE
                        
                        # Only draw if submerged
                        if ORIENTATION == 1 and local_bx < (global_liquid_x - screen_start_x - bubble_slosh):
                            draw.ellipse((local_bx, b.y, local_bx + b.size, b.y + b.size), outline="black", fill="black")
                        elif ORIENTATION == -1 and local_bx > (128 - (global_liquid_x - screen_start_x - bubble_slosh)):
                            draw.ellipse((local_bx, b.y, local_bx + b.size, b.y + b.size), outline="black", fill="black")

            time.sleep(SCREEN_DELAY)