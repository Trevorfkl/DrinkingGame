# animations.py
from bubbles import bubbles_fill # We can still use our bubble logic

def play_animation(mux, screens, mode, value=None):
    if mode == "timer_fill":
        # Example: Fill 3 screens over 5 seconds
        bubbles_fill(mux, screens, duration=5, quantity=3)
        
    elif mode == "shot_pour":
        # A quick splash for a shot
        bubbles_fill(mux, screens, duration=1, quantity=1)
        
    elif mode == "victory":
        # Custom logic for winning - maybe fill all 5 very fast
        bubbles_fill(mux, screens, duration=0.5, quantity=5)
        
    else:
        print("Unknown animation mode!")