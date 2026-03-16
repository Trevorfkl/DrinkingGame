import time
import random
from luma.core.render import canvas

# --- CONFIGURATION VARIABLES ---
# Set 1 for Left-to-Right, -1 for Right-to-Left
FLOW_DIRECTION = 1 
# Change this to True to "drain" the beer instead of filling it
UNFILL_MODE = False 
# Delay between the signal reaching the next screen (in seconds)
SCREEN_DELAY = 0.002 

class BigBubble:
    def __init__(self, total_width):
        self.total_width = total_width
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.total_width)
        self.y = random.randint(0, 32)
        self.size = random.randint(2, 5) # Bigger bubbles
        self.speed_x = random.uniform(1.0, 3.0) * FLOW_DIRECTION

    def move(self):
        self.x += self.speed_x
        if self.x < -20 or self.x > self.total_width + 20:
            self.reset()

def run(mux, screens):
    num_screens = len(screens)
    total_width = 128 * num_screens
    # Global X tracks the "front" of the beer from 0 to 640
    global_liquid_x = 0 if not UNFILL_MODE else total_width
    
    bubbles = [BigBubble(total_width) for _ in range(30)]

    while True:
        # 1. Update Global Liquid Position
        step = 2.5 # Speed of the flow
        if not UNFILL_MODE:
            if global_liquid_x < total_width: global_liquid_x += step
            else: time.sleep(1.5); global_liquid_x = 0 # Reset
        else:
            if global_liquid_x > 0: global_liquid_x -= step
            else: time.sleep(1.5); global_liquid_x = total_width

        # 2. Update Bubbles
        for b in bubbles:
            b.move()

        # 3. Render to Screens sequentially
        for i, (device, channel) in enumerate(screens):
            mux.select_channel(channel)
            
            # Map global X to this screen's local 0-128 range
            # Screen 0: 0-127, Screen 1: 128-255, etc.
            screen_start_x = i * 128
            screen_end_x = screen_start_x + 127
            
            # Calculate how much of THIS screen is full
            if global_liquid_x > screen_start_x:
                # Local fill is global position minus where this screen starts
                local_fill_x = min(128, global_liquid_x - screen_start_x)
                
                with canvas(device) as draw:
                    # Draw the Beer Sweep
                    # If we are in Flow Direction 1, we fill from left. 
                    # If -1, we would fill from right (logic below)
                    if FLOW_DIRECTION == 1:
                        draw.rectangle((0, 0, local_fill_x, 32), outline="white", fill="white")
                    else:
                        draw.rectangle((128 - local_fill_x, 0, 128, 32), outline="white", fill="white")

                    # Draw Bubbles only if they are on this screen AND submerged
                    for b in bubbles:
                        if screen_start_x <= b.x <= screen_end_x:
                            local_bx = b.x - screen_start_x
                            # Only draw if bubble is "inside" the beer
                            is_submerged = (local_bx < local_fill_x) if FLOW_DIRECTION == 1 else (local_bx > (128 - local_fill_x))
                            if is_submerged:
                                draw.ellipse((local_bx, b.y, local_bx + b.size, b.y + b.size), outline="black", fill="black")
            
            else:
                # If the liquid hasn't reached this screen yet, keep it black
                with canvas(device) as draw:
                    pass
            
            # This is your requested 2ms delay between hardware updates
            time.sleep(SCREEN_DELAY)