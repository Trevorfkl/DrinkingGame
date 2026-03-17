import time
from luma.core.render import canvas

# --- SAFE MODE SETTINGS ---
SCREEN_ORDER = [5, 4, 3, 2, 1]
# Turn this down to 100kHz equivalent speed in code
SCREEN_DELAY = 0.005 

def run(mux, screens):
    num_screens = len(SCREEN_ORDER)
    # A single bar moving across the screens
    pos = 0
    screen_map = {channel: device for device, channel in screens}

    while True:
        pos = (pos + 4) % (128 * num_screens)
        
        for i, ch in enumerate(SCREEN_ORDER):
            if ch not in screen_map: continue
            
            mux.select_channel(ch)
            device = screen_map[ch]
            start_x = i * 128
            
            # Draw ONLY if the position is within this screen
            with canvas(device) as draw:
                local_x = pos - start_x
                if 0 <= local_x <= 128:
                    # Just a simple vertical line - the easiest thing to draw
                    draw.line((local_x, 0, local_x, 32), fill="white")
            
            time.sleep(SCREEN_DELAY)