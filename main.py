# Version 0.3.0

from machine import Pin
from i2c_responder import I2CResponder
from pico_lights import pico_light_controller
from time import sleep, sleep_ms
from machine import UART
import json
from debug import debugger

# Set True for debug output and functions
debugEnable = True

debug = debugger(debugEnable)

# Format a value or list of values as 2 digit hex.
def format_hex(_object):
    try:
        values_hex = [to_hex(value) for value in _object]
        return '[{}]'.format(', '.join(values_hex))
    except TypeError:
        # The object is a single value
        return to_hex(_object)

def to_hex(value):
    return '0x{:02X}'.format(value)

def send_serial(serial, serialdata):
  serial.write(serialdata.encode('utf-8'))
  return 0

# Config UART serial
UARTbaud = 115200
UARTtx = Pin(4)
UARTrx = Pin(5)

# Init UART serial
serial = UART(1, baudrate=UARTbaud, tx=UARTtx, rx=UARTrx)
debug.print(str(serial))

# Config I2C
I2C_FREQUENCY = 100000
RESPONDER_I2C_DEVICE_ID = 0
RESPONDER_ADDRESS = 0x41
GPIO_RESPONDER_SDA = 16
GPIO_RESPONDER_SCL = 17

# Initialize I2C Responder
debug.print("Init I2C")
i2c_port = I2CResponder(RESPONDER_I2C_DEVICE_ID, sda_gpio=GPIO_RESPONDER_SDA, scl_gpio=GPIO_RESPONDER_SCL, responder_address=RESPONDER_ADDRESS)
debug.print(str(i2c_port))

debug.print("Init lights module")
lights = pico_light_controller(debug, i2c_port, RESPONDER_ADDRESS)
debug.print(str(lights))

# Init onboard LED
debug.print("Init onboard LED")
led = Pin(25, Pin.OUT)
lights.flash(led, 1)

# Init program loop vars
data = []

# Main program loop
debug.print("Starting program loop")

while True:
    
    # check for I2C data - Load into data var until transfer complete
    i2c_data = lights.read_i2c()
    if len(i2c_data) > 0:
        lights.flash(led, 1)
        for byte in i2c_data:
            data.append(byte)
        debug.print("received I2C data")
        debug.print(str(i2c_data))

    #When no buffer data pending and data var contains command data to process
    elif data:
        debug.print("I2C data read into buffer")

        # 0b00xxxxxx: Reserved
        # 0b01GRIIII 0bDDDDDDDD - set light or light group duty cycle
        # 0b1xxxxxxx: Get/set config data
        
        # Get / set config data
        if data[0] & 0b10000000:
            debug.print("Command: Get / set config data")

            result = lights.get_set_config(data)
        
        # Set a value command
        elif data[0] & 0b01000000:

            debug.print("Command: Setting a light or group value")

            result = lights.set_lights(data)

        # Reserved function
        else:
            debug.print("Command: Reserved")
            returnByte = bytearray(1)
            lights.send_i2c(returnByte)
            lights.flash(led, 1)
    
        #reset program loop vars
        debug.print("clearing data vars")
        data = []
            
    #Nothing to do this loop
    else:
        pass
    
    #Check for quit command on UART
    serialdata = serial.read()

    if serialdata == b'quit':
        debug.print("quitting")
        break