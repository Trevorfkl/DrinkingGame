import time
import bubbles
import victory
from smbus2 import SMBus
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c

# 1. Manual Multiplexer Controller
class TCA9548A:
    def __init__(self, bus, address=0x70):
        self.bus = bus
        self.address = address

    def select_channel(self, channel):
        if 0 <= channel <= 7:
            # Writing the channel bit to the multiplexer
            self.bus.write_byte(self.address, 1 << channel)

# 2. Hardware Initialization
def init_hardware():
    print("Initializing hardware...")
    bus = SMBus(1)  # Open I2C bus 1
    mux = TCA9548A(bus)
    
    screens = []
    for ch in range(5):
        print(f"Connecting to Screen on Channel {ch}...")
        mux.select_channel(ch)
        # We use a dummy wrapper so luma thinks it's talking to a real port
        serial = i2c(port=1, address=0x3C) 
        device = ssd1306(serial, width=128, height=32)
        screens.append((device, ch)) # Keep track of the channel
        
    return mux, screens

# 3. The Brain Logic
def main():
    print("--- Brain Initialized ---")
    mux, screens = init_hardware()
    
    try:
        while True:
            # We pass the MUX so the animation can switch channels
            bubbles.run(mux, screens)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()