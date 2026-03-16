# display_setup.py
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.multiplexer import TCA9548A

def get_screens():
    """Initializes the multiplexer and returns a list of 5 screen objects."""
    try:
        serial = i2c(port=1, address=0x70)
        multiplexer = TCA9548A(serial)
        
        # Create a list of 5 screens on channels 0 through 4
        screens = [ssd1306(multiplexer.get_device(ch), width=128, height=32) for ch in range(5)]
        return screens
    except Exception as e:
        print(f"Hardware Error: {e}")
        return None