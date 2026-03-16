import time
import random
from luma.core.render import canvas

class Bubble:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x, self.y = random.randint(0, 128), 40
        self.size, self.speed = random.randint(2, 5), random.uniform(1.0, 3.5)
    def move(self):
        self.y -= self.speed
        if self.y < -10: self.reset()

def run(screens):
    all_bubbles = [[Bubble() for _ in range(6)] for _ in range(5)]
    while True: 
        for i, device in enumerate(screens):
            with canvas(device) as draw:
                for bubble in all_bubbles[i]:
                    bubble.move()
                    draw.ellipse((bubble.x, bubble.y, bubble.x + bubble.size, bubble.y + bubble.size), outline="white")
        time.sleep(0.02)