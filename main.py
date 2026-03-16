import bubbles
import victory
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from luma.core.multiplexer import TCA9548A

def init_hardware():
    serial = i2c(port=1, address=0x70)
    multiplexer = TCA9548A(serial)
    return [ssd1306(multiplexer.get_device(ch), width=128, height=32) for ch in range(5)]

def main():
    print("--- Brain Initialized ---")
    screens = init_hardware()
    # For now, it just runs bubbles. Later we will add the "If drinking" logic here.
    bubbles.run(screens)

if __name__ == "__main__":
    main()