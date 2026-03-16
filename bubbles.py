# bubbles.py
import time
import random
from luma.core.render import canvas

class Bubble:
    def __init__(self):
        self.reset()

    def reset(self):
        # Bubbles start at the bottom and float up
        self.x = random.randint(0, 128)
        self.y = random.randint(32, 60) 
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.8, 2.0)

    def move(self, current_liquid_line):
        self.y -= self.speed
        # Reset if it floats above the beer surface or the top of screen
        if self.y < current_liquid_line:
            self.reset()

def run(mux, screens):
    # liquid_line starts at 0 (top) and moves to 32 (bottom)
    liquid_line = 0 
    
    # 8 bubbles per screen
    all_bubbles = [[Bubble() for _ in range(8)] for _ in range(len(screens))]

    while True:
        # 1. Update Liquid Level (The Fill)
        if liquid_line < 32:
            liquid_line += 0.2  # Adjust this to change fill speed
        
        # 2. Update Bubbles
        for i in range(len(screens)):
            for b in all_bubbles[i]:
                b.move(0) # In this mode, bubbles float to the very top (0)

        # 3. Draw to each screen
        for i, (device, channel) in enumerate(screens):
            mux.select_channel(channel)
            
            with canvas(device) as draw:
                # Draw the "Beer" filling from top to bottom
                # rectangle((x0, y0, x1, y1))
                if liquid_line > 0:
                    draw.rectangle((0, 0, 128, int(liquid_line)), outline="white", fill="white")
                
                # Draw Bubbles (as black dots inside the white beer)
                for b in all_bubbles[i]:
                    if b.y < liquid_line:
                        draw.point((b.x, b.y), fill="black")
        
        time.sleep(0.01)