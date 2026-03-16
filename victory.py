import time
from luma.core.render import canvas

def run(screens, duration=5):
    end_time = time.time() + duration
    while time.time() < end_time:
        for device in screens:
            with canvas(device) as draw:
                draw.rectangle(device.bounding_box, outline="white", fill="white")
        time.sleep(0.1)
        for device in screens:
            with canvas(device) as draw:
                pass 
        time.sleep(0.1)