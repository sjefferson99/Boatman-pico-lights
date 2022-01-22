from machine import Pin
import time
from i2c_responder import I2CResponder


I2C_FREQUENCY = 100000

RESPONDER_I2C_DEVICE_ID = 0
RESPONDER_ADDRESS = 0x41
GPIO_RESPONDER_SDA = 16
GPIO_RESPONDER_SCL = 17

READBUFFER = [0, 0]

led = Pin(25, Pin.OUT)

def main():

    # -----------------
    # Initialize Responder
    # -----------------
    i2c_responder = I2CResponder(
        RESPONDER_I2C_DEVICE_ID, sda_gpio=GPIO_RESPONDER_SDA, scl_gpio=GPIO_RESPONDER_SCL, responder_address=RESPONDER_ADDRESS
    )

print(I2CResponder)

i = 0

while i < 5:
    print("Looping {}".format(i))
    led.on()
    time.sleep_ms(100)
    led.off()
    time.sleep(1)
    i += 1

led.on()