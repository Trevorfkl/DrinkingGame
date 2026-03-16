# bubbles.py
import time
import random
from luma.core.render import canvas

class Bubble:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x, self.y = random.randint(0, 128), 40
        self.size, self.speed = random.randint(2, 5), random.uniform(2.0, 4.5)
    def move(self):
        self.y -= self.speed
        if self.y < -10: self.reset()

def run(mux, screens):
    # Initialize bubbles for 5 screens
    all_bubbles = [[Bubble() for _ in range(6)] for _ in range(5)]
    
    while True:
        for i, (device, channel) in enumerate(screens):
            # Switch the multiplexer to the correct screen
            mux.select_channel(channel)
            
            with canvas(device) as draw:
                for b in all_bubbles[i]:
                    b.move()
                    draw.ellipse((b.x, b.y, b.x + b.size, b.y + b.size), outline="white")
        time.sleep(0.001) # Speed it up for the Pi 4