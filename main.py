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
    print("Initializing hardware (Channels 1-5)...")
    bus = SMBus(1)
    mux = TCA9548A(bus)
    screens = []
    
    # We change the range to (1, 6) which means 1, 2, 3, 4, 5
    for ch in range(1, 6):
        print(f"Connecting to Screen on Channel {ch}...")
        mux.select_channel(ch)
        time.sleep(0.1) # Vital "breather" for the hardware
        
        try:
            serial = i2c(port=1, address=0x3C)
            device = ssd1306(serial, width=128, height=32)
            screens.append((device, ch))
            print(f"Success: Screen {ch} is alive!")
        except Exception as e:
            print(f"Error on Channel {ch}: {e}")
            
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
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping Game...")
        # Tell the Mux to disconnect all channels on exit
        bus = SMBus(1)
        bus.write_byte(0x70, 0) 
    except Exception as e:
        print(f"Crash: {e}")
        bus = SMBus(1)
        bus.write_byte(0x70, 0)