import time
import random
from luma.core.render import canvas

# --- CONTROL PANEL ---
# Physical order of screens on your arm (e.g., [5, 4, 3, 2, 1] or [1, 2, 3, 4, 5])
SCREEN_ORDER = [5, 4, 3, 2, 1] 
# Direction of flow WITHIN each screen: 1 for left-to-right, -1 for right-to-left
ORIENTATION = 1 
# Set to True to start full and empty out (Drinking Mode)
UNFILL_MODE = False 
# Delay between the signal reaching the next screen
SCREEN_DELAY = 0.002 

class BigBubble:
    def __init__(self, total_width):
        self.total_width = total_width
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.total_width)
        self.y = random.randint(0, 32)
        self.size = random.randint(2, 5) 
        self.speed_x = random.uniform(1.0, 3.5) * ORIENTATION

    def move(self):
        self.x += self.speed_x
        if self.x < -20 or self.x > self.total_width + 20:
            self.reset()
            self.x = 0 if ORIENTATION == 1 else self.total_width

def run(mux, screens):
    num_screens = len(SCREEN_ORDER)
    total_width = 128 * num_screens
    
    # Global state
    global_liquid_x = 0 if not UNFILL_MODE else total_width
    bubbles = [BigBubble(total_width) for _ in range(35)]

    # Create a map to find the right screen object based on our desired order
    # screens is a list of (device, channel)
    screen_map = {channel: device for device, channel in screens}

    while True:
        # 1. Update Liquid Progression
        fill_speed = 3.0
        if not UNFILL_MODE:
            if global_liquid_x < total_width: global_liquid_x += fill_speed
            else: time.sleep(1.5); global_liquid_x = 0 
        else:
            if global_liquid_x > 0: global_liquid_x -= fill_speed
            else: time.sleep(1.5); global_liquid_x = total_width

        # 2. Update Bubbles
        for b in bubbles:
            b.move()

        # 3. Draw to Screens in the specified PHYSICAL order
        for i, physical_channel in enumerate(SCREEN_ORDER):
            if physical_channel not in screen_map:
                continue
                
            device = screen_map[physical_channel]
            mux.select_channel(physical_channel)
            
            # Map global X (0-640) to this specific screen's window
            screen_start_x = i * 128
            screen_end_x = screen_start_x + 127
            
            # Determine if the liquid has reached this screen yet
            if global_liquid_x > screen_start_x:
                local_fill_x = min(128, global_liquid_x - screen_start_x)
                
                with canvas(device) as draw:
                    # Draw the "Beer"
                    if ORIENTATION == 1:
                        draw.rectangle((0, 0, local_fill_x, 32), outline="white", fill="white")
                    else:
                        draw.rectangle((128 - local_fill_x, 0, 128, 32), outline="white", fill="white")

                    # Draw Big Bubbles
                    for b in bubbles:
                        if screen_start_x <= b.x <= screen_end_x:
                            local_bx = b.x - screen_start_x
                            is_submerged = (local_bx < local_fill_x) if ORIENTATION == 1 else (local_bx > (128 - local_fill_x))
                            if is_submerged:
                                draw.ellipse((local_bx, b.y, local_bx + b.size, b.y + b.size), outline="black", fill="black")
            else:
                # Still empty
                with canvas(device) as draw:
                    pass
            
            time.sleep(SCREEN_DELAY)