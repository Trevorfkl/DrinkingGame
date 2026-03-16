import time
import random
from luma.core.render import canvas

class Bubble:
    def __init__(self):
        self.reset()

    def reset(self):
        # Bubbles now spawn at the right side or within the beer
        self.x = random.randint(0, 128)
        self.y = random.randint(0, 32)
        # Bigger bubbles as requested
        self.size = random.randint(2, 4) 
        # Move right-to-left to simulate flow
        self.speed_x = random.uniform(-2.0, -0.5)
        self.jitter_y = random.uniform(-1.0, 1.0)

    def move(self):
        self.x += self.speed_x
        self.y += self.jitter_y
        
        # Reset if it goes off screen or gets too high/low
        if self.x < -10 or self.y < -5 or self.y > 37:
            self.reset()
            self.x = 130 # Spawn back at the far right

def run(mux, screens):
    liquid_x = 0 
    # More bubbles, and they are bigger now
    all_bubbles = [[Bubble() for _ in range(12)] for _ in range(len(screens))]

    while True:
        # 1. Update Fill Progress (The Sweep)
        if liquid_x < 128:
            liquid_x += 0.4 # Sweep speed
        else:
            time.sleep(2)
            liquid_x = 0 # Reset pour

        # 2. Draw to each screen
        for i, (device, channel) in enumerate(screens):
            mux.select_channel(channel)
            
            # Update bubble positions for this screen
            for b in all_bubbles[i]:
                b.move()

            with canvas(device) as draw:
                # 3. Draw the "Beer" Sweep
                # We add a little 'sin' wave or random jitter to the leading edge
                edge_turbulence = random.randint(-2, 2)
                draw.rectangle((0, 0, int(liquid_x) + edge_turbulence, 32), outline="white", fill="white")
                
                # 4. Draw Bigger Bubbles
                for b in all_bubbles[i]:
                    # Only draw bubble if it's "submerged" in the beer sweep
                    if b.x < liquid_x:
                        # Draw as a circle (ellipse) instead of a point for "Big" look
                        draw.ellipse((b.x, b.y, b.x + b.size, b.y + b.size), outline="black", fill="black")
        
        time.sleep(0.01)